"""
This module uses regex to extract important information from text extracted from docket PDFs.
"""

# in-built or third party libs
import re
import logging
from typing import Dict

# project modules


def parse_main(text: str = "") -> Dict:

    """
    Parse texted from PDFs using regex.

    Each time we extract docket text from PDF the results can be slightly
    different.

    However there are generally specific words that precede and proceed the
    text we want. We use these markers in our regex.
    """
    if text == "":
        logging.warning("Empty string provided for parsing")

    return {
        "charges": extract_charges(text),
        "bail": extract_bail(text),
        "arresting_agency": extract_arresting_agency()
    }


def extract_charges(text: str) -> str:

    """ Returns list of charges from raw text. Note: some charges may not be
     extracted perfectly """

    # attempt tp parse text file for charges
    try:
        # PARSE
        logging.info("Attempting to extract charges from text with Regex...")
        pattern = re.compile(
            r"(Grade Description\n)"  # look for 'Grade Description' first
            r"((F\d?|M\d?|S)?\n)*"  # May be followed by multiple M, F1, etc.
            r"(?P<charges_text>.*?)"  # our charges text - we capture this
            r"(\nOffense Dt|\nCHARGES|\nDISPOSITION|\nDisposition|\nFiled "
            r"Date|\nM\d?\n|\nF\d?\n|\nS\n|\nBail Set:\n|\nPage |\n# "
            r"Charge\n)",  # wide range of keywords proceed charges
            re.DOTALL,  # matches all chars, including newlines
        )
        match = pattern.search(text)
        charges = match.group("charges_text")  # we used named capture group
        logging.info(f"CHARGES, FIRST PASS: {charges}")

        # CLEAN UP
        logging.info("Cleaning up charges text...")
        charges = charges.replace(
            "\n", "; "
        )  # Replacing newline chars so data looks better in table
        charges = charges[0:400]  # Limit size of captured text

    # If something goes wrong with parsing, default to None
    except AttributeError as e:
        logging.info(
            "Parsing failed or couldn't find target value - setting " "to None"
        )
        charges = None

    logging.info(f"CHARGES, FINAL: {charges}")
    return charges


def extract_bail(text: str) -> int:

    """ Returns bail amount from raw text, eg. '1200'. Note: unlike charges,
    many dockets will have no bail set. Most values will return as None"""

    # parsing text file for bail
    try:
        # PARSE
        logging.info("Attempting to extract bail from text with Regex...")
        pattern = re.compile(
            r"(Amount\n)"  # first find 'Amount' and newline
            r"\$" r"((\d|,)*)"  # capture all digits and commas
            r"\.00",  # end with '.00'
            re.DOTALL,
        )
        match = pattern.search(text)
        bail = match.group(2)
        logging.info(f"BAIL, FIRST PASS: {bail}")

        # CLEAN UP
        bail = bail[0:15]  # limit size
        bail = bail.replace("\n", "").replace(",", "")  # remove newlines,
        # commas
        bail = int(bail)  # return as int

    # If something goes wrong with parsing, default to None. We could set to
    # 0 here but we prefer None because not all offenses result in bail
    # being set. Using '0' may imply a bail of $0 was set.
    except (AttributeError, ValueError) as e:
        logging.info(
            "Parsing failed or couldn't find target value - setting " "to None"
        )
        bail = None

    logging.info(f"BAIL, FINAL: {bail}")
    return bail


def extract_arresting_agency(text: str) -> str:

    """ Returns bail amount from raw text, eg. '1200'. Note: unlike charges,
    many dockets will have no bail set. Most values will return as None"""

    # parsing text file for bail
    try:
        # PARSE
        logging.info("Attempting to extract bail from text with Regex...")
        pattern = re.compile(
            r"\n[A-Z]\s\d{4,}.*\n(?P<agency>.*(Police|PSP|police|District "
            r"Attorney|district attorney).*)\n"
        )
        match = pattern.search(text)
        agency = match.group('agency')
        logging.info(f"ARRESTING AGENCY, FIRST PASS: {agency}")


    # If something goes wrong with parsing, default to None
    except AttributeError as e:
        logging.info(
            "Parsing failed or couldn't find target value - setting " "to None"
        )
        agency = None

    logging.info(f"ARRESTING AGENCY, FINAL: {agency}")
    return agency
