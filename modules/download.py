"""
This module downloads dockets as PDFs and stores them in a given directory
"""

# Third party or inbuilt libs
import time
import logging
# Project modules
from modules.misc import pdf_path_gen
from locations import dirs


def download_pdf(driver, docket_url, docketnum):

    # SET PATHS
    path_downloaded_docket = (
        dirs["pdfs"] / "MDJReport.pdf"
    )  # path of our file when it's first downloaded
    new_path_downloaded_docket = pdf_path_gen(
        dirs["pdfs"], docketnum
    )  # path we will rename our filename with

    # DOWNLOAD
    logging.info("Downloading docket sheet PDF for: {}".format(docketnum))
    logging.info("URL: {}".format(docket_url))
    try:
        driver.get(docket_url)
    except Exception as e:
        logging.error("Something went wrong with PDF download")
        logging.exception(e)
        driver.quit()
        raise

    # Waiting a small amount of time and checking to see whether file exists every few milliseconds.
    # This addresses bug where program was attemping to rename file before it had finished downloading.
    # This is a hacky workaround but Stack Overflow suggests that it's one way to deal with how Selenium downloads files. In future,
    # may need to replace this with a better solution.
    counter = 0
    cycles = 120
    sleep_interval = 0.1
    logging.info(
        f"Waiting max of {cycles * sleep_interval} seconds for file " f"to appear..."
    )
    while counter < cycles and not path_downloaded_docket.is_file():
        logging.debug(
            f"cycle: {counter}, time: {round((counter * sleep_interval), 1)} sec"
        )
        time.sleep(sleep_interval)
        counter += 1
    if path_downloaded_docket.is_file():
        logging.info("Download complete")
    else:
        # This is a serious error - it may mean UJS website isn't available
        logging.error("PDF file didn't appear during download")
        driver.quit()
        raise

    # RENAME FILENAME
    # Renaming file so downloaded PDFs are easy to organize and search if needed
    logging.info("Renaming file")
    logging.info("Old path: {}".format(path_downloaded_docket))
    path_downloaded_docket.rename(new_path_downloaded_docket)
    logging.info("New path: {}".format(new_path_downloaded_docket))
    return new_path_downloaded_docket
