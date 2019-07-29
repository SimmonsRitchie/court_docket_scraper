"""
NAME: Pa Court Report
AUTHOR: Daniel Simmons-Ritchie

ABOUT:
This file is the entrypoint. From main(), the program performs the following actions:

    -DELETE + CREATE: temp folders from earlier scrapes are deleted and recreated
    -SCRAPE: UJS website is accessed and basic info on district dockets are scraped from search results
    -DOWNLOAD: After initial scrape, PDFs with more info for each docket are downloaded.
    -CONVERT: PDFs are converted into text and other info is extracted.
    -DATA EXPORT: Scraped data is turned into different formats for export,
    eg html, csv.
    -MOVE (OPTIONAL): If enabled, data will be moved to an AWS S3 bucket.
    -UPLOAD (OPTIONAL): If enabled, data will be uploaded to a REST API
    -EMAIL: A summary of data is emailed to desired recipients.

NOTE: Due to the way ChromeDriver downloads PDFs in this program, it was
designed to run in headless mode (set as default).
Attempting to run it in non-headless mode may cause it to crash.

"""
# inbuilt or third party libs
import os
import json
import logging
from datetime import datetime

# Project modules
from modules import initialize, scrape, download, convert, email, export, upload, misc
from modules.misc import get_datetime_now_formatted
from modules.parse import parse_main
from modules.scrape import scrape
from modules.move_s3 import copy_file_to_s3_bucket
from locations import dirs, temp_dir, paths
from logs.config.logging import logs_config


def main():

    ########################################################################
    #                                 SETUP
    ########################################################################

    # INIT LOGGING
    logs_config()

    # START TIME
    scrape_start_time = datetime.now()

    # GET ENV VARS
    county_list = json.loads(os.environ.get("COUNTY_LIST"))
    target_scrape_day = os.environ.get("TARGET_SCRAPE_DATE", "yesterday").lower()
    target_scrape_date = (
        misc.today_date() if target_scrape_day == "today" else misc.yesterday_date()
    )  # convert to date
    scrape_name = os.getenv("SCRAPE_NAME", "Cases Scrape")
    run_env = os.environ.get("ENV_FILE", "DEV")  # defaults to 'DEV'
    rest_api_enabled = os.getenv("REST_API_ENABLED")
    rest_api_enabled = True if rest_api_enabled == "TRUE" else False
    move_to_s3_enabled = os.getenv("MOVE_TO_S3_ENABLED")
    move_to_s3_enabled = True if move_to_s3_enabled == "TRUE" else False

    # REFORMAT COUNTY LIST
    county_list = [
        x.title() for x in county_list
    ]  # Counties are transformed into print_title case, otherwise we'll get errors during scrape

    ########################################################################
    #                          START PROGRAM
    ########################################################################

    misc.print_title("pa court report")
    logging.info("##### PROGRAM START #####")
    logging.info(f"Scrape: {scrape_name}")
    logging.info(f"Running in {run_env} environment\n")

    ########################################################################
    #                          DELETE + CREATE
    ########################################################################

    # DELETE OLD FILES
    # If temp folder was created from previous scrape we delete it so it doesn't cause complications.
    misc.delete_folders_and_contents(temp_dir)

    # CREATE TEMP DIRECTORIES
    temp_subdirs = [
        dirs[directory]
        for directory in dirs
        if "/" + str(temp_dir.name) + "/" in str(dirs[directory])
    ]
    misc.create_folders(temp_subdirs)

    ########################################################################
    #                                 SCRAPE
    ########################################################################

    for county in county_list:

        # SCRAPE UJS SEARCH RESULTS
        # We first get basic docket data from search results, like docket
        # numbers, filing dates, etc. and turn it into a list of dicts.
        docket_list = scrape(county, target_scrape_date)
        if docket_list:

            # DOWNLOAD PDF OF EACH DOCKET
            # Each case is associated with a PDF that has more data. We
            # extract info from those pdfs and add them to our dicts.
            driver = initialize.initialize_driver()
            for docket in docket_list:
                pdf_path = download.download_pdf(
                    driver, docket["url"], docket["docketnum"]
                )
                text = convert.convert_pdf_to_text(pdf_path, docket["docketnum"])

                # PARSE PDF TEXT
                parsed_data = parse_main(text)
                docket.update(parsed_data)
            driver.quit()

            # CONVERT DICT LIST INTO PANDAS DF
            df = export.convert_dict_into_df(docket_list, county)

            # SAVE BACKUP OF DF FOR DEBUGGING
            df.to_pickle(dirs["df_pkl"] / "df.pkl")

            # CONVERT DF TO CSV
            export.convert_df_to_csv(df)

            # CONVERT DF INTO HTML FOR EMAIL PAYLOAD
            county_intro = "{} in {} County:".format(
                df.shape[0], county
            )  # count of cases
            html_df = export.convert_df_to_html(df)
            export.save_html_county_payload(county_intro, html_df)

        else:
            logging.info(f"No cases were found for {county} County")
            county_intro = f"No cases found for {county} County."
            export.save_html_county_payload(county_intro)

    ########################################################################
    #                        EXPORT & EMAIL FINAL PAYLOAD
    ########################################################################

    # START TIME
    scrape_end_time = datetime.now()

    # OPTIONAL: MOVE JSON FILE TO S3
    if move_to_s3_enabled:
        export.convert_csv_to_json(scrape_end_time, county_list)
        copy_file_to_s3_bucket()

    # OPTIONAL: UPLOAD DATA TO DATABASE
    if rest_api_enabled and paths["payload_csv"].is_file():
        upload.upload_to_rest_api()

    # SEND EMAIL WITH DOCKET DATA
    email.email_notification(scrape_start_time, scrape_end_time,
                             target_scrape_day,
                             county_list)

    # CLOSE PROGRAM
    logging.info("Scrape completed at: {}".format(get_datetime_now_formatted()))
    logging.info("Closing program")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # Terminating program and sending email notification
        error_summary = "An unexpected error occurred"
        logging.critical(error_summary)
        logging.exception(e)
        try:
            email.email_error_notification(error_summary, e)
        except Exception as e:
            logging.exception(e)
        finally:
            raise SystemExit
