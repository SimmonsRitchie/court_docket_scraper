"""
This module stores small, reusable functions used by other modules. Eg. getting dates, formatting dates, creating directory and file paths

"""

from datetime import datetime, timedelta
import os
from shutil import rmtree


def pdf_path_gen(dir, docketnum):
    """
    We need to dynamically generate file names for downloaded PDFs We use this function so
    paths are always created in a consistent format.
    """
    return dir / "{}.pdf".format(docketnum)


def extracted_text_path_gen(dirs, docketnum):
    """
    We need to dynamically generate file names for downloaded PDFs We use this function so
    paths are always created in a consistent format.
    """
    return dirs["extracted_text"] / "{}.txt".format(docketnum)


def check_directory_exists(base_folder):
    directory = os.path.dirname(base_folder)
    if not os.path.exists(directory):
        os.makedirs(directory)


def yesterday_date():
    yesterday = datetime.now() - timedelta(1)
    return yesterday.strftime("%m%d%Y")


def today_date():
    today = datetime.now()
    return today.strftime("%m%d%Y")


def formatted_yesterday_date():
    yesterday = datetime.now() - timedelta(1)
    return yesterday.strftime("%m/%d/%Y")


def formatted_yesterday_date_name():
    yesterday = datetime.now() - timedelta(1)
    yesterday = yesterday.strftime("%a, %b %-d %Y")
    return yesterday


def currency_convert(x):
    if str(x) == "nan":
        x = ""
        return x
    elif type(x) == float or type(x) == int:
        x = "${:,.0f}".format(x)
        return x
    else:
        return ""


def camel_case_convert(item):
    item = (
        item.title().replace(" ", "").replace("_", "").replace("-", "")
    )  # removing all '_', '-', and spaces
    item = item[0].lower() + item[1:] if item else ""
    return item


def delete_folders_and_contents(list_of_dirs):

    """
    Takes a dict of directories as Path objects, deletes each one if it exists.

    """

    print("Checking that temp files have been deleted from previous scraper runs")

    for dir in list_of_dirs:

        if dir.is_dir():
            print("Deleting {}...".format(dir))
            try:
                rmtree(dir)
                print("Successfully deleted the directory and all files inside")
            except OSError:
                print(f"Deletion of the directory {dir} failed for some reason")
        else:
            print("No folder named {} detected".format(dir))


def create_folders(list_of_dirs):
    """
    Takes a dict of directories as Path objects, creates each one

    """
    for dir in list_of_dirs:
        dir.mkdir(parents=False, exist_ok=False)
