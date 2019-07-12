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
from locations import test_dirs, temp_dir, test_paths

def main():

    ########################################################################
    #                                 SETUP
    ########################################################################

    # SET DIRECTORY NAMES
  # temporary directory for files/folders created during scrape
    temp_subdirs = [
        test_dirs["pdfs"],
        test_dirs["extracted_text"],
        test_dirs["payload_email"],
        test_dirs["payload_csv"],
        test_dirs["payload_json"],
        test_dirs["email_final"]
    ]

    # ENV VARS
    county_list = json.loads(os.environ.get("COUNTY_LIST"))
    target_scrape_day = os.environ.get("TARGET_SCRAPE_DATE", "yesterday").lower()
    target_scrape_date = (
        misc.today_date() if target_scrape_day == "today" else misc.yesterday_date()
    )  # convert to date

    # ENV VARS - OPTIONAL
    run_env = os.environ.get("ENV_FILE", "DEV")  # defaults to 'DEV'

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
    # If temp folder was created from previous scrape we delete it so it doesn't cause complications.
    misc.delete_folders_and_contents(temp_dir)

    # CREATE TEMP DIRECTORIES
    temp_subdirs = [dir for dir in test_dirs if temp_dir.name in str(dir)]
    misc.create_folders(temp_subdirs)

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
            driver, county, target_scrape_date
        )
        if docket_list:

            # CYCLE THROUGH LIST OF DICTS, DOWNLOAD PDF OF EACH DOCKET
            # Each case is associated with a PDF that has more data. We now download each PDF using URLs we
            # scraped from the search results.
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
    date_and_time_of_scrape = export.convert_csv_to_json(county_list)

    # OPTIONAL: UPLOAD DATA TO DATABASE
    # if REST API env vars are set and data exists, then convert csv to json and upload to it using post request.
    if os.getenv("REST_API_HOSTNAME") and test_paths["payload_csv"].is_file():
        upload.upload_to_rest_api()

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
