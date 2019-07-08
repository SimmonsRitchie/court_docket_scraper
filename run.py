"""
NAME: Pa Court Report
AUTHOR: Daniel Simmons-Ritchie

ABOUT:
This is the main file for the program. From main(), the program performs the following actions.

    -DELETE: files from earlier scrapes are deleted (ie. all files in 'pdfs','extracted_text','json_payload','csv_payload' folders).
    -INITIALIZE: Selenium webdriver is initialized.

    Program begins looping through each county specified in the county_list in config.py and does the following:

        -SCRAPE: UJS website is accessed using selenium and basic info on today's district dockets for that county are scraped from search results.
        -DOWNLOAD: After scraping, PDFs of each docket are downloaded for that county.
        -CONVERT: PDFs are converted into text and other info is extracted for that county's dockets (eg. bail, charges).
        -DATA ADDED TO TEXT FILE: Scraped data for that county is added to a HTML formatted text file in preparation for being emailed at end of program run.
        -DATA ADDED TO CSV FILE: Scraped data for that county is added to a CSV file.

    -EXPORT TO JSON: A json file is created from the CSV file (which now has scraped data from all counties).
    -EMAIL: The email payload text file is emailed to selected email addresses specified in config.py.

NOTE: Due to the way this program downloads PDFs, it was designed to run in headless mode (ie. without a visible browser). Attempting to run it in non-headless mode may cause it to crash.


"""
# inbuilt or third party libs
import os
import json
# Project modules
from modules import delete, initialize, scrape, download, convert, email, export, misc


def main():
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
    destination_email_addresses = json.loads(os.environ.get("DESTINATION_EMAIL_ADDRESSES"))
    sender_email_username = os.environ.get("SENDER_EMAIL_USERNAME")
    sender_email_password = os.environ.get("SENDER_EMAIL_PASSWORD")
    target_scrape_day = os.environ.get("TARGET_SCRAPE_DATE", "yesterday").lower() # "yesterday" or "today"
    target_scrape_date = misc.today_date() if target_scrape_day == "today" else misc.yesterday_date() # convert to date

    # REFORMAT COUNTY LIST
    county_list = [
        x.title() for x in county_list
    ]  # Counties are transformed into title case, otherwise we'll get errors during scrape

    # DELETE OLD FILES
    list_of_folders_to_delete = [
        base_folder_pdfs,
        base_folder_email,
        base_folder_json,
        base_folder_csv,
        base_folder_text,
        base_folder_final_email,
    ]
    delete.delete_temp_files(list_of_folders_to_delete)

    # START CHROME DRIVER
    driver = initialize.initialize_driver(base_folder_pdfs, chrome_driver_path)

    # SCRAPE UJS SEARCH RESULTS - SAVE DATA AS LIST OF DICTS
    # We first get basic docket data, like case caption and filing date, from search results.
    for county in county_list:
        docket_list = scrape.scrape_search_results(
            driver, url, county, target_scrape_date
        )

        # CYCLE THROUGH LIST OF DICTS, DOWNLOAD PDF OF EACH DOCKET
        # PDF dockets have more info than search results. We want to scrape date from those too so we can add it to our final payload.
        for count, docket in enumerate(docket_list):
            docket_num = docket["docket_num"]
            docket_url = docket["url"]
            download.download_pdf(driver, docket_url, docket_num, base_folder_pdfs)
            text = convert.convert_pdf_to_text(
                docket_num, base_folder_pdfs, base_folder_text
            )

            # PARSE PDF TEXT FOR CHARGES AND BAIL, ADD VALUES TO EACH DICT
            if text:
                parseddata = convert.parse_extracted_text(text)
                docket["charges"] = parseddata["charges"]
                docket["bail"] = parseddata["bail"]
            else:
                print("Error: no extracted text found") # if no text, it likely means that there was a problem converting PDF to text
                docket["charges"] = "error: check docket"
                docket["bail"] = "error: check docket"

        # CONVERT DICT LIST INTO PANDAS DF
        # We convert the data to a df because it makes it easier to work with it convert it into different formats
        df = export.convert_dict_into_df(docket_list, county)

        # CONVERT DF INTO HTML FOR EMAIL PAYLOAD
        export.payload_generation(
            base_folder_email,
            base_folder_email_template,
            df,
            county
        )

        # CONVERT DF TO CSV
        export.convert_df_to_csv(df, base_folder_csv)

    # CREATE JSON FILE FROM CSV
    date_and_time_of_scrape = export.convert_csv_to_json(
        base_folder_csv, base_folder_json, county_list
    )

    # UPLOAD JSON TO DATABASE
    # TODO: Add function to upload to database

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
