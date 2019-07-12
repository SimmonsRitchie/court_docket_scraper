"""
NAME: Pa Court Report
AUTHOR: Daniel Simmons-Ritchie

ABOUT:
This is the entrypoint for the program. From main(), the program performs the following actions:

    -DELETE + CREATE: temp folders from earlier scrapes are deleted and recreated
    -INITIALIZE: Selenium webdriver is initialized.
    -SCRAPE: UJS website is accessed and basic info on district dockets are scraped from search results
    -DOWNLOAD: After initial scrape, PDFs with more info for each docket are downloaded.
    -CONVERT: PDFs are converted into text and other info is extracted for that county's dockets.
    -DATA EXPORT: Scraped data is turned into different formats for export.
    -UPLOAD (OPTIONAL): If REST API settings are given in .env, data will be uploaded to REST API
    -EMAIL: A summary of data is emailed to desired recipients.

NOTE: Due to the way ChromeDriver downloads PDFs, it was designed to run in headless mode (set as default).
Attempting to run it in non-headless mode may cause it to crash.

"""
# inbuilt or third party libs
import os
from pathlib import Path
import json

# Project modules
from modules import initialize, scrape, download, convert, email, export, upload, misc


def main():

    ########################################################################
    #                                 SETUP
    ########################################################################

    # SET DIRECTORY NAMES
    temp_dir = Path(
        "temp/"
    )  # temporary directory for files/folders created during scrape
    temp_subdirs = [
        "pdfs",
        "extracted_text",
        "payload_email",
        "payload_csv",
        "payload_json",
        "email_final",
    ]
    dirs = {}
    for dir in temp_subdirs:  # generating temp subdirectories and stashing in a dict
        dirs[dir] = temp_dir / dir
    dirs["email_template"] = Path(
        "static/email_template"
    )  # static directory with HTML for email payload

    # SET PATHS
    # Temp files that we will need to read and write to multiple times throughout program run.
    paths = {
        "payload_email": dirs["payload_email"] / "email.html",
        "payload_csv": dirs["payload_csv"] / "dockets.csv",
        "payload_json": dirs["payload_json"] / "dockets.json",
        "email_final": dirs["email_final"] / "email.html",
    }

    # ENV VARS - REQUIRED
    # these values need to be set in .env file
    county_list = json.loads(os.environ.get("COUNTY_LIST"))
    target_scrape_day = os.environ.get("TARGET_SCRAPE_DATE", "yesterday").lower()
    target_scrape_date = (
        misc.today_date() if target_scrape_day == "today" else misc.yesterday_date()
    )  # convert to date

    # ENV VARS - OPTIONAL
    run_env = os.environ.get("ENV_FILE", "DEV")  # defaults to 'DEV'
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
    #                          START PROGRAM
    ########################################################################

    misc.title("pa court report")
    print(f"Running in {run_env} environment\n")

    ########################################################################
    #                          DELETE + CREATE
    ########################################################################

    # DELETE OLD FILES
    # To avoid complications, we delete any temp folders that may have been created from previous scrapes.
    misc.delete_folders_and_contents(temp_dir)

    # CREATE TEMP DIRECTORIES
    misc.create_folders(dirs, temp_subdirs)

    ########################################################################
    #                                 SCRAPE
    ########################################################################

    # START CHROME DRIVER
    driver = initialize.initialize_driver()

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
            for docket in docket_list:
                docketnum = docket["docketnum"]
                docket_url = docket["url"]
                pdf_path = download.download_pdf(driver, docket_url, docketnum)
                text = convert.convert_pdf_to_text(pdf_path, docketnum)

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
            export.convert_df_to_csv(df)

            # CONVERT DF INTO HTML FOR EMAIL PAYLOAD
            county_intro = "{} in {} County:".format(
                df.shape[0], county
            )  # count of cases
            html_df = export.convert_df_to_html(df)
            export.save_html_county_payload(county_intro, html_df)

        # IF NO DATA RETURNED FROM SCRAPE...
        else:
            county_intro = "No cases found for {} County.".format(
                county
            )  # count of cases in county
            export.save_html_county_payload(
                county_intro)  # save html df + add extra html

    ########################################################################
    #                        EXPORT & EMAIL FINAL PAYLOAD
    ########################################################################

    # CREATE JSON FILE FROM CSV
    # We create a json file with some metadata about scrape.
    date_and_time_of_scrape = export.convert_csv_to_json(paths, county_list)

    # OPTIONAL: UPLOAD DATA TO DATABASE
    # if REST API env vars are set and data exists, then convert csv to json and upload to it using post request.
    if rest_api["hostname"] and paths["payload_csv"].is_file():
        upload.upload_to_rest_api(rest_api, paths)

    # SEND EMAIL WITH DOCKET DATA
    email.email_notification(
        date_and_time_of_scrape,
        target_scrape_day,
        county_list
    )

    # CLOSE PROGRAM
    print("Closing program")


# Start main loop if running from program.py
if __name__ == "__main__":
    main()
