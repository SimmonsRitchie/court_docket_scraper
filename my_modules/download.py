"""
This module downloads dockets as PDFS and stores them in a folder
"""

# Other modules
import os
import time

# My modules
from my_modules import misc


def download_pdf(driver, docket_url, docket_num, base_folder_pdfs):
    misc.check_directory_exists(base_folder_pdfs)
    old_name = os.path.join(base_folder_pdfs,"MDJReport.pdf")
    new_name = misc.pdf_path_generator(base_folder_pdfs, docket_num)
    print("Downloading docket sheet PDF for: {}".format(docket_num))
    print("URL: {}".format(docket_url))
    try:
        driver.get(docket_url)
    except:
        print("ERROR: Something went wrong with download")
        print("Closing program")
        driver.quit()
        quit()

    # Checking to see whether file exists every few milliseconds.
    # This addresses issue where program was attemping to rename file before it had finished downloading.
    counter = 0
    while counter < 10 and not os.path.exists(old_name):
        print("Waiting for file to appear... {}".format(counter))
        time.sleep(0.05)
        counter += 1
    if os.path.exists(old_name):
        print("Download complete!\n")
    else:
        print("ERROR: Something went wrong, file didn't appear")
        print("Closing program")
        driver.quit()
        quit()

    # Renaming file and continuing program as normal
    print("Renaming file")
    print("Old path: {}".format(old_name))
    print("New path: {}".format(new_name))
    os.rename(old_name, new_name)
