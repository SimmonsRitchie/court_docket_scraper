"""
This module uses regex to extract important information from text extracted from docket PDFs.
"""

# in-built or third party libs
import re
import logging

# project modules



def parse_main(text):

    """
    Parse texted from PDFs using regex.

    :param text: Text to search
    :return: dictionary with desired values
    """

    charges = extract_charges(text)
    bail = extract_bail(text)

    return {
        "charges": charges,
        "bail": bail
        }

def extract_charges(text):
    # parsing text file for charges
    try:
        logging.info("Attempting to extract charges from text with Regex...")
        pattern = re.compile(
            r"(Grade Description\n)((F|F1|F2|F3|M|M1|M2|M3|S)?\n)*(.*?)(\nOffense "
            r"Dt|\nCHARGES|\nDISPOSITION|\nDisposition|\nFiled Date)",
            re.DOTALL,
        )
        match = pattern.search(text)
        charges = match.group(4)
        logging.info(f"CHARGES, FIRST CUT: {charges}")
        charges = charges.replace(
            "\n", "; "
        )  # Replacing newline characters so easier to display data in tabular format
        charges = charges[0:400]  # Limit size of captured text
        logging.info(f"CHARGES, FINAL CUT: {charges}")
        return charges
    except AttributeError as e:
        logging.warning("Something went wrong with charges parsing")
        logging.exception(e)
        charges = None
        logging.info(f"CHARGES, FINAL CUT: {charges}")
        return charges

def extract_bail(text):
    # parsing text file for bail
    try:
        logging.info("Attempting to extract bail from text with Regex...")
        pattern = re.compile(r"(Amount\n)\$(.*)\.00", re.DOTALL)
        match = pattern.search(text)
        bail = match.group(2)
        logging.info(f"BAIL, FIRST CUT: {bail}")
        # Removing newline characters
        bail = bail[0:15]
        bail = bail.replace("\n", "").replace(",", "")
        logging.info(f"BAIL, FINAL CUT: {bail}")
        return bail
    except (AttributeError, ValueError) as e:
        logging.warning("Something went wrong with bail parsing for that docket")
        logging.exception(e)
        bail = None
        logging.info(f"BAIL, FINAL CUT: {bail}")
        return bail