"""
This module downloads dockets as PDFs and stores them in a given directory
"""

# Third party or inbuilt libs
import os
import time

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
    print("Downloading docket sheet PDF for: {}".format(docketnum))
    print("URL: {}".format(docket_url))
    try:
        driver.get(docket_url)
    except:
        print("ERROR: Something went wrong with download")
        print("Closing program")
        driver.quit()
        quit()

    # Waiting a small amount of time and checking to see whether file exists every few milliseconds.
    # This addresses bug where program was attemping to rename file before it had finished downloading.
    # This is a hacky workaround but Stack Overflow suggests that it's one way to deal with how Selenium downloads files. In future,
    # may need to replace this with a better solution.
    counter = 0
    while counter < 120 and not path_downloaded_docket.is_file():
        print("Waiting for file to appear... {}".format(counter))
        time.sleep(0.1)
        counter += 1
    if path_downloaded_docket.is_file():
        print("Download complete!\n")
    else:
        print("ERROR: Something went wrong, file didn't appear")
        print("Closing program")
        driver.quit()
        quit()

    # RENAME FILENAME
    # Renaming file so downloaded PDFs are easy to organize and search if needed
    print("Renaming file")
    print("Old path: {}".format(path_downloaded_docket))
    path_downloaded_docket.rename(new_path_downloaded_docket)
    print("New path: {}".format(new_path_downloaded_docket))
    return new_path_downloaded_docket
