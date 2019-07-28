"""
This module uses regex to find important information from text extracted
from docket PDFs.
"""

# in-built or third party libs
import re
import logging
from typing import Dict, Pattern, Callable, Any, Optional, Union


def charges_clean_up(charges):
    """ Returns cleaned charges. Charges are typically separated by newlines
    and can often be in all caps, which we want to avoid."""

    charges = charges.split("\n")
    charges = [charge.capitalize() for charge in charges]
    charges = "; ".join(charges)
    # we want some acronyms to be in caps for readability
    charges = re.sub("(?i)dui", "DUI", charges)
    return charges


"""
PARSER RECIPE
We set how different text fields will be parsed here.
"""
parser_recipe = [
    {
        "field": "charges",
        "pattern": re.compile(
            r"(Grade Description\n)"  # look for 'Grade Description' first
            r"((F\d?|M\d?|S)?\n)*"  # May be followed by multiple M, F1...
            r"(?P<charges>.*?)"
            r"(\nOffense Dt|\nCHARGES|\nDISPOSITION|\nDisposition|\nFiled "
            r"Date|\nM\d?\n|\nF\d?\n|\nS\n|\nBail Set:\n|\nPage |\n# "
            r"Charge\n)",  # wide range of keywords proceed charges
            re.DOTALL,  # matches all chars, including newlines
        ),
        "clean_up": charges_clean_up,
        "limit_size": 400,
    },
    {
        "field": "bail",
        "pattern": re.compile(
            r"(Amount\n)"  # first find 'Amount' and newline
            r"\$"
            r"(?P<bail>(\d|,)*)"  # capture all digits and commas
            r"\.00",  # end with '.00'
            re.DOTALL,
        ),
        "type_converter": lambda x: int(x),
        "clean_up": lambda x: x.replace(",", ""),
        "limit_size": 15,
    },
    {
        "field": "arresting_agency",
        "pattern": re.compile(
            r"\n[A-Z]\s\d{4,}.*"  # OTN number, eg. U 725538-2
            r"\n(?P<arresting_agency>.*(Police|PSP|police|District "
            r"Attorney|district attorney|Detectives|detectives| "
            r"PD|Inspector General|Attorney General|Sheriff|Amtrak).*)\n"
        ),
        "limit_size": 100,
    },
    {
        "field": "municipality",
        "pattern": re.compile(
            r"\w*\n"  # typically county name, eg. Dauphin
            r"(?P<municipality>[a-zA-Z ]*)\n"
            r"CASE INFORMATION\n"
        ),
        "limit_size": 100,
    },
    {
        "field": "defendant",
        "pattern": re.compile(
            r"Commonwealth of Pennsylvania\n"
            r"v.\n"
            r"(?P<defendant>.*)\n"
        ),
        "limit_size": 100,
    },
    {
        "field": "defendant_gender",
        "pattern": re.compile(
            r"(Sex:\n)?"  # often precedes gender but not always
            r"(Race:\n)?"  # often precedes gender but not always
            r"(?P<defendant_gender>Male|Female)\n"
        ),
        "limit_size": 20,
    },    {
        "field": "defendant_race",
        "pattern": re.compile(
            r"(Sex:\n)?" # often precedes race but not always
            r"(Race:\n)?" # often precedes race but not always
            r"(Male|Female)\n"
            r"(?P<defendant_race>White|Black|Hispanic|Asian|Native "
            r"American|Unknown/Unreported)\n"
        ),
        "limit_size": 50,
    },
]


def parse_main(text: str = "") -> Dict:

    """
    A loop for processing each parsing recipe. Returns a dict of parsed values.
    """
    if text == "":
        logging.warning("Empty string provided for parsing")

    parsed_data = {}
    for recipe in parser_recipe:
        field = recipe["field"]
        parsed_data[field] = parser(text, **recipe)
    return parsed_data


def parser(
    text: str,
    *,
    field: str,
    pattern: Pattern[str],
    type_converter: Optional[Callable] = None,
    clean_up: Optional[Callable] = None,
    limit_size: Optional[int] = None,
    null_value: Optional[Union[str, int, bool, None]] = None,
) -> str:
    """
    Returns text based on regex pattern and other provided conditions.

    :param text: Str. Text to parse.
    :param field: Str. Label for output info, eg 'charges', 'bail'.
    :param pattern: Pattern. Regex, compiled pattern used to search.
    :param type_converter: Callable. Optional. Set type for return value.
    Defaults to string converter.
    :param clean_up: Callable. Optional. Function that does any final
    formatting.
    :param limit_size: Int. Optional. Max number of chars in returned string.
    :param null_value: Any. Optional. Value to set when parse conditions
    aren't met. 
    Default None.
    :return: Str. Desired pattern in text.
    """
    # set default if no type converter func is provided
    if not type_converter:
        type_converter = lambda x: str(x)

    # parse
    logging.info("Attempting to extract charges from text with Regex...")
    try:
        match = pattern.search(text)
        final_value = match.group(field)
        logging.info(f"{field.upper()}, FIRST PASS: {final_value}")

        # Options
        if clean_up:
            final_value = clean_up(final_value)
        if limit_size:
            final_value = final_value[0:limit_size]
        # Trim
        final_value = final_value.strip()
        # Type
        final_value = type_converter(final_value)

    except (AttributeError, ValueError) as e:
        logging.info(
            "Parsing failed or couldn't find target value - setting " "to None"
        )
        final_value = null_value

    logging.info(f"{field.upper()}, FINAL: {final_value}")
    return final_value
