"""
This module stores small, reusable functions used by other modules.
Eg. getting dates, formatting dates, creating directory and file paths

"""

from datetime import datetime, timedelta
import os
from shutil import rmtree
import pandas as pd
import logging
from typing import Union, Optional, List
from pathlib import Path
import re


def print_title(program_name: str) -> None:
    print("----------------------------------------------------------------")
    print("                  {}".format(program_name.upper()))
    print("----------------------------------------------------------------")


def get_datetime_now_formatted() -> str:
    """ Gets a string of the current date and time
    in format: Jul 11 2019: 1:28 PM"""
    return datetime.now().strftime("%b %d %Y, %-I:%M %p")


def gen_unique_filename(
    directory: Path, filename: str, ext: str, counter: Optional[int] = 0
) -> Path:
    """
    This func recursively determines if a filename already exists in a given
    directory. Returns a unique path.
    It expects directory to be a Path object.
    """
    full_filename = (
        filename + ext if counter == 0 else filename + "_" + str(counter) + ext
    )
    path = directory / full_filename
    logging.info(f"Checking if {path} already exists...")
    if path.is_file():
        counter += 1
        logging.info(f"{path} exists")
        logging.info(f"Appending {counter} to filename")
        return gen_unique_filename(directory, filename, ext, counter=counter)
    logging.info(f"{path} is unique")
    return path


def pdf_path_gen(directory: Path, docketnum: str) -> Path:
    """
    Dynamically generates file names for downloaded PDF.
    """
    return gen_unique_filename(directory, docketnum, ".pdf")


def extracted_text_path_gen(directory: Path, docketnum: str) -> Path:
    """
    Dynamically generates file names for text extracted from PDF.
    """
    return gen_unique_filename(directory, docketnum, ".txt")


def yesterday_date() -> str:
    """Generates yesterday's date in format needed for input in UJS portal"""
    yesterday = datetime.now() - timedelta(1)
    return yesterday.strftime("%m%d%Y")


def today_date() -> str:
    """Generates yesterday's date in format needed for input in UJS portal"""
    today = datetime.now()
    return today.strftime("%m%d%Y")


def camel_case_convert(item: str) -> str:
    """Converts strings that look_like_this to
    strings that lookLikeThis"""

    item = (
        item.title().replace(" ", "").replace("_", "").replace("-", "")
    )  # removing all '_', '-', and spaces
    item = item[0].lower() + item[1:] if item else ""
    return item


def delete_folders_and_contents(temp_dir: Path) -> None:

    """Takes Path directory, deletes directory if it exists."""

    if temp_dir.is_dir():
        logging.info("Detected temp files from previous program run")
        logging.info("Deleting folders and files...")
        rmtree(temp_dir)
        logging.info("Deleted")
    else:
        logging.info("No temp files detected - project directory clean")


def create_folders(dirs: List[Path]):
    """
    Takes a dict of directories as Path objects, creates each one

    """
    logging.info("Generating temp directories:")
    for dir in dirs:
        dir.mkdir(parents=True)  # creates folder and parent folders if
        # they don't exist
        logging.info(">> {}".format(dir))
    logging.info("Temp directories created")


def clean_list_of_dicts(list_of_dicts):
    """
    Take a list of dicts and returns a list of dicts. Any dict that had
    duplicate docketnums is removed. Retains the
    first record in a duplicated set.
    """
    df = pd.DataFrame(list_of_dicts)
    df = clean_df(df)
    return df.to_dict("records")


def clean_df(df):
    """
    Returns a df with NaN or NaTs replaced with None. Also removes any records
    with duplicate docketnums (retains the first record of a set of duplicates)
    """
    if not df.empty:  # df must not be empty otherwise Pandas will throw error
        df = df[~df.duplicated(subset="docketnum", keep="first")]
        df = df.where(pd.notnull(df), None)  # Replace NaN values with None
        df["dob"] = df["dob"].replace({"NaT": None})  # Replace NaT values with None
        df["filing_date"] = df["filing_date"].replace(
            {"NaT": None}
        )  # Replace NaT values with None
    return df


def detect_keyword_in_df(df: pd.DataFrame, column: str, keyword: str) -> str:
    """ Detects whether a word/phrase exists in a particular column of a
    Pandas df and then returns a string identifying how many times that
    keyword was detected for each county in the df"""

    # DETECT KEYWORD
    df = df[df[column].str.contains(keyword, flags=re.IGNORECASE)]
    df = df.groupby(["county"]).size().reset_index(name="counts")
    counties = df["county"].unique()
    if len(counties) > 0:
        counties = [county.capitalize() for county in counties]
        if len(counties) == 1:
            counties_formatted = "{} County".format(counties[0])
        else:
            counties_formatted = "{} Counties".format(", ".join(counties))
        return "{} ({})".format(keyword.capitalize(), counties_formatted)


def highlight_row_in_df(s, keyword_list, column):
    """
    Highlights a row of a pandas dataframe if a selected column (or columns)
    contains a keyword (or keywords)

    :param s: Obj. Dataframe.
    :param keyword_list: List of strings. Keywords that you want to search.
    :param column: List of strings. Columns you want to search
    :return: Returns formatting for row if selected column contains selected keyword.
    """
    # cwe first convert list into 'safe' form in case it has '!' or '?' or
    # other
    # special regex chars
    safe_keyword_list = [re.escape(m) for m in keyword_list]
    keyword_regex = "|".join(safe_keyword_list)
    is_max = pd.Series(data=False, index=s.index)
    is_max[column] = s.loc[column].str.contains(keyword_regex,
                                                flags=re.IGNORECASE)
    return ['background-color: #fccc8d' if is_max.any() else ''
            for v in is_max]