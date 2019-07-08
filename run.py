"""
NAME: Pa Court Report
AUTHOR: Daniel Simmons-Ritchie

ABOUT:
This is the entrypoint for the program. From main(), the program performs the following actions:

    -DELETE: files from earlier scrapes are deleted (ie. all files in 'pdfs','extracted_text','json_payload',
    'csv_payload' folders).
    -INITIALIZE: Selenium webdriver is initialized.
    -SCRAPE: UJS website is accessed and basic info on district dockets are scraped from search results
    -DOWNLOAD: After initial scrape, PDFs of each docket are downloaded.
    -CONVERT: PDFs are converted into text and other info is extracted for that county's dockets (eg. bail, charges).
    -DATA EXPORT: Scraped data is turned into different formats for export.
    -UPLOAD (OPTIONAL): If REST API settings are given in .env, data will be uploaded to REST API
    -EMAIL: A summary of data is emailed to desired recipients.

NOTE: Due to the way ChromeDriver downloads PDFs, it was designed to run in headless mode (set as default).
Attempting to run it in non-headless mode may cause it to crash.


"""
# inbuilt or third party libs
import os
import json

# Project modules
from modules import (
    delete,
    initialize,
    scrape,
    download,
    convert,
    email,
    export,
    upload,
    misc,
)


def main():

    ########################################################################
    #                                 SETUP
    ########################################################################

    url = "https://ujsportal.pacourts.us/DocketSheets/MDJ.aspx"  # URL for UJC website

    # SET DIRECTORY PATHS
    base_folder_pdfs = "pdfs/"
    base_folder_email = "email_payload/"
    base_folder_json = "json_payload/"
    base_folder_csv = "csv_payload/"
    base_folder_text = "extracted_text/"
    base_folder_email_template = "email_template/"
    base_folder_final_email = "email_final/"

    # GET CONFIG OPTIONS FROM ENV VARIABLES
    chrome_driver_path = os.environ.get("CHROME_DRIVER_PATH")
    county_list = json.loads(os.environ.get("COUNTY_LIST"))
    destination_email_addresses = json.loads(
        os.environ.get("DESTINATION_EMAIL_ADDRESSES")
    )
    sender_email_username = os.environ.get("SENDER_EMAIL_USERNAME")
    sender_email_password = os.environ.get("SENDER_EMAIL_PASSWORD")
    target_scrape_day = os.environ.get(
        "TARGET_SCRAPE_DATE", "yesterday"
    ).lower()  # "yesterday" or "today"
    target_scrape_date = (
        misc.today_date() if target_scrape_day == "today" else misc.yesterday_date()
    )  # convert to date

    # OPTIONAL: REST API VARS
    # These vars are used to upload data to REST API. If .env vars are blank, we'll ignore.
    rest_api = {
        "hostname": os.environ.get("REST_API_HOSTNAME"),
        "login_endpoint": os.environ.get("LOGIN_END_POINT"),
        "logout_endpoint": os.environ.get("LOGOUT_END_POINT"),
        "post_endpoint": os.environ.get("POST_END_POINT"),
        "username": os.environ.get("REST_API_USERNAME"),
        "password": os.environ.get("REST_API_PASSWORD"),
    }

    # REFORMAT COUNTY LIST
    county_list = [
        x.title() for x in county_list
    ]  # Counties are transformed into title case, otherwise we'll get errors during scrape

    ########################################################################
    #                                 DELETE
    ########################################################################

    # DELETE OLD FILES
    # To avoid complications, we delete all temp folders created from previous scrapes.
    list_of_folders_to_delete = [
        base_folder_pdfs,
        base_folder_email,
        base_folder_json,
        base_folder_csv,
        base_folder_text,
        base_folder_final_email,
    ]
    delete.delete_temp_files(list_of_folders_to_delete)

    ########################################################################
    #                                 SCRAPE
    ########################################################################

    # START CHROME DRIVER
    driver = initialize.initialize_driver(base_folder_pdfs, chrome_driver_path)

    # SCRAPE UJS SEARCH RESULTS - SAVE DATA AS LIST OF DICTS
    # We first get basic docket data from search results, like docket numbers, filing dates, and URLs to download
    # PDFs of full docket data.
    for county in county_list:
        docket_list = scrape.scrape_search_results(
            driver, url, county, target_scrape_date
        )
        if docket_list:

            # CYCLE THROUGH LIST OF DICTS, DOWNLOAD PDF OF EACH DOCKET
            # We now download each docket's full PDF file using the URL we just scraped. We get extra info and add
            # it to our docket dicts.
            for count, docket in enumerate(docket_list):
                docket_num = docket["docket_num"]
                docket_url = docket["url"]
                download.download_pdf(driver, docket_url, docket_num, base_folder_pdfs)
                text = convert.convert_pdf_to_text(
                    docket_num, base_folder_pdfs, base_folder_text
                )

                # PARSE PDF TEXT FOR EXTRA INFO
                if text:
                    parsed_data = convert.parse_extracted_text(text)
                    docket["charges"] = parsed_data["charges"]
                    docket["bail"] = parsed_data["bail"]
                else:
                    print(
                        "Error: no extracted text found"
                    )  # if no text, it likely means that there was a problem converting PDF to text
                    docket["charges"] = "error: check docket"
                    docket["bail"] = "error: check docket"

            # CONVERT DICT LIST INTO PANDAS DF
            df = export.convert_dict_into_df(docket_list, county)

            # CONVERT DF TO CSV
            export.convert_df_to_csv(df, base_folder_csv)

            # CONVERT DF INTO HTML FOR EMAIL PAYLOAD
            county_intro = "{} in {} County:".format(
                df.shape[0], county
            )  # count of cases
            html_df = export.convert_df_to_html(df)
            export.save_html_county_payload(
                county_intro, base_folder_email, base_folder_email_template, html_df
            )

        # IF NO DATA RETURNED FROM SCRAPE...
        else:
            county_intro = "No cases found for {} County.".format(
                county
            )  # count of cases in county
            export.save_html_county_payload(
                county_intro, base_folder_email, base_folder_email_template
            )  # save html df + add extra html

    ########################################################################
    #                        EXPORT & EMAIL FINAL PAYLOAD
    ########################################################################

    # CREATE JSON FILE FROM CSV
    # We create a json file with some metadata about scrape.
    date_and_time_of_scrape = export.convert_csv_to_json(
        base_folder_csv, base_folder_json, county_list
    )

    # OPTIONAL: UPLOAD DATA TO DATABASE
    # if REST API env vars are set, then convert csv to json and upload to it using post request.
    if rest_api["hostname"]:
        upload.upload_to_rest_api(rest_api)

    # SEND EMAIL WITH DOCKET DATA
    email.email_notification(
        base_folder_email,
        base_folder_email_template,
        base_folder_final_email,
        destination_email_addresses,
        sender_email_username,
        sender_email_password,
        date_and_time_of_scrape,
        target_scrape_day,
        county_list,
    )

    # CLOSE PROGRAM
    print("Closing program")


# Start main loop if running from program.py
if __name__ == "__main__":
    main()
