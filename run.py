"""
NAME: Pa. court docket scraper
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

NOTE1: This was one of the author's earliest coding projects. Some of the code is a bit wacky or redundant
(in particular the use of collections in the 'scrape' module).

NOTE2: Due to the way this program downloads PDFs, it was designed to run in headless mode (ie. without a visible browser). Attempting to run it in non-headless mode may cause it to crash.

NOTE3: Make sure you have version 0.23 or higher of Pandas installed. This program makes use of .hide_index() on styled dataframes,
a relatively new feature.

"""
# Third party libs
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

    # GET ENVIRON VARIABLES
    chrome_driver_path = os.environ.get("CHROME_DRIVER_PATH")
    county_list = json.loads(os.environ.get("COUNTY_LIST"))
    destination_email_addresses = json.loads(os.environ.get("DESTINATION_EMAIL_ADDRESSES"))
    sender_email_username = os.environ.get("SENDER_EMAIL_USERNAME")
    sender_email_password = os.environ.get("SENDER_EMAIL_PASSWORD")
    target_scrape_date = misc.today_date() if os.environ.get("TARGET_SCRAPE_DATE").lower() == "today" else misc.yesterday_date()

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

    # SCRAPE DOCKET DATA FOR EACH COUNTY
    for county in county_list:
        docketdata = scrape.scrape_search_results(
            driver, url, county, target_scrape_date
        )

        # IF THERE'S DATA THEN DOWNLOAD PDF AND EXTRACT TEXT FOR EACH DOCKET
        if docketdata:
            charges_list = []
            bail_list = []
            for x, y in enumerate(docketdata.docket_num):
                docket_num = docketdata.docket_num[x]
                docket_url = docketdata.docket_url[x]
                download.download_pdf(driver, docket_url, docket_num, base_folder_pdfs)
                text = convert.convert_pdf_to_text(
                    docket_num, base_folder_pdfs, base_folder_text
                )

                # PARSE EXTRACTED PDF TEXT FOR CHARGES AND BAIL
                if text:
                    parseddata = convert.parse_extracted_text(text)
                    charges_list.append(parseddata.charge)
                    bail_list.append(parseddata.bail)
                else:
                    print("Error: no extracted text found")
                    charges_list.append("Error: Check docket")
                    bail_list.append("Error: check docket")
                print("Clean version of extracted charge and bail:")
                print(docket_num)
                print(parseddata.charge)
                print(parseddata.bail)

        # CREATE DICT OF DATA - DATA IS STORED AS LIST OF VALUES FOR EACH KEY
        data_in_dictionary_format = {
            "Name": docketdata.case,
            "Filing date": docketdata.filing_date,
            "DOB": docketdata.dob,
            "Charges": charges_list,
            "Bail": bail_list,
            "URL": docketdata.docket_url,
        }

        # CONVERT LIST OF DICTS INTO HTML FOR EMAIL PAYLOAD (ALSO CREATES CSV)
        export.payload_generation(
            base_folder_email,
            base_folder_csv,
            base_folder_email_template,
            data_in_dictionary_format,
            county,
        )

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
        target_scrape_date,
        county_list,
    )

    # CLOSE PROGRAM
    print("Closing program")


# Start main loop if running from program.py
if __name__ == "__main__":
    main()
