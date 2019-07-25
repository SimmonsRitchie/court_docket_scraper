"""
NAME: Pa Court Report
AUTHOR: Daniel Simmons-Ritchie

ABOUT:
This file is the entrypoint. From main(), the program performs the following actions:

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
import json
import logging

# Project modules
from modules import initialize, scrape, download, convert, email, export, upload, misc
from modules.misc import get_datetime_now_formatted
from modules.parse import parse_main
from modules.scrape import scrape
from locations import dirs, temp_dir, paths
from logs.config.logging import logs_config


def main():

    ########################################################################
    #                                 SETUP
    ########################################################################

    # INIT LOGGING
    logs_config()

    # GET ENV VARS
    county_list = json.loads(os.environ.get("COUNTY_LIST"))
    target_scrape_day = os.environ.get("TARGET_SCRAPE_DATE", "yesterday").lower()
    target_scrape_date = (
        misc.today_date() if target_scrape_day == "today" else misc.yesterday_date()
    )  # convert to date
    scrape_name = os.getenv("SCRAPE_NAME","Cases Scrape")
    run_env = os.environ.get("ENV_FILE", "DEV")  # defaults to 'DEV'
    rest_api_enabled = os.getenv("REST_API_ENABLED")
    rest_api_enabled = True if rest_api_enabled == "TRUE" else False

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
        # numbers, filing dates
        docket_list = scrape(county, target_scrape_date)
        if docket_list:

            # DOWNLOAD PDF OF EACH DOCKET
            # Each case is associated with a PDF that has more data. We now
            # download and parse each PDF
            driver = initialize.initialize_driver()
            for docket in docket_list:
                pdf_path = download.download_pdf(
                    driver, docket["url"], docket["docketnum"]
                )
                text = convert.convert_pdf_to_text(pdf_path, docket["docketnum"])

                # PARSE PDF TEXT FOR EXTRA INFO
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

    # CREATE JSON FILE FROM CSV
    # We save a json file with some metadata about scrape.
    date_and_time_of_scrape = export.convert_csv_to_json(county_list)

    # OPTIONAL: UPLOAD DATA TO DATABASE
    if rest_api_enabled and paths["payload_csv"].is_file():
        upload.upload_to_rest_api()

    # SEND EMAIL WITH DOCKET DATA
    email.email_notification(date_and_time_of_scrape, target_scrape_day, county_list)

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
