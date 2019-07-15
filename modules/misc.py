"""
This module stores small, reusable functions used by other modules. Eg. getting dates, formatting dates, creating directory and file paths

"""

from datetime import datetime, timedelta
import os
from shutil import rmtree
import pandas as pd
import logging

def print_title(program_name):
    print("----------------------------------------------------------------")
    print("                  {}".format(program_name.upper()))
    print("----------------------------------------------------------------")

def get_datetime_now_formatted():
    """ Gets a string of the current date and time in format: Jul 11 2019: 1:28 PM"""
    return datetime.now().strftime("%b %d %Y, %-I:%M %p")


def gen_unique_filename(dir, filename, ext, counter=0):
    """
    This func recursively determines if a filename already exists in a given directory. Returns a unique path.
    It expects dir to be a Path object.
    """
    full_filename = (
        filename + ext if counter == 0 else filename + "_" + str(counter) + ext
    )
    path = dir / full_filename
    logging.info(f"Checking if {path} already exists...")
    if path.is_file():
        counter += 1
        logging.info(f"{path} exists")
        logging.info(f"Appending {counter} to filename")
        return gen_unique_filename(dir, filename, ext, counter=counter)
    logging.info(f"{path} is unique")
    return path


def pdf_path_gen(dir, docketnum):
    """
    Dynamically generates file names for downloaded PDF.
    """
    return gen_unique_filename(dir, docketnum, ".pdf")


def extracted_text_path_gen(dir, docketnum):
    """
    Dynamically generates file names for text extracted from PDF.
    """
    return gen_unique_filename(dir, docketnum, ".txt")


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


def delete_folders_and_contents(temp_dir):

    """Takes Path directory, deletes directory if it exists."""

    if temp_dir.is_dir():
        logging.info("Detected temp files from previous program run")
        logging.info("Deleting folders and files...")
        rmtree(temp_dir)
        logging.info("Deleted")
    else:
        logging.info("No temp files detected - project directory clean")


def create_folders(dirs):
    """
    Takes a dict of directories as Path objects, creates each one

    """
    logging.info("Generating temp directories:")
    for dir in dirs:
        dir.mkdir(parents=True)  # creates folder and parent folders if they don't exist
        logging.info(">> {}".format(dir))
    logging.info("Temp directories created")


def clean_list_of_dicts(list_of_dicts):
    """
    Take a list of dicts and returns a list of dicts. Any dict that had duplicate docketnums is removed. Retains the
    first record in a duplicated set.
    """
    df = pd.DataFrame(list_of_dicts)
    df = clean_df(df)
    return df.to_dict("records")


def clean_df(df):
    """
    Returns a df with NaN or NaTs replaced with None. Also removes any records with duplicate docketnums (
    retains the first record of a set of duplicates)
    """
    if not df.empty:  # df must not be empty otherwise Pandas will throw error
        df = df[~df.duplicated(subset="docketnum", keep="first")]
        df = df.where(pd.notnull(df), None)  # Replace NaN values with None
        df["dob"] = df["dob"].replace({"NaT": None})  # Replace NaT values with None
        df["filing_date"] = df["filing_date"].replace(
            {"NaT": None}
        )  # Replace NaT values with None
    return df
