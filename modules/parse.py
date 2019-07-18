"""
This module uses regex to extract important information from text extracted
from docket PDFs.
"""

# in-built or third party libs
import re
import logging
from typing import Dict, Pattern, Callable, Any, Optional, Union

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
            r"(?P<charges>.*?)"  # we capture this
            r"(\nOffense Dt|\nCHARGES|\nDISPOSITION|\nDisposition|\nFiled "
            r"Date|\nM\d?\n|\nF\d?\n|\nS\n|\nBail Set:\n|\nPage |\n# "
            r"Charge\n)",  # wide range of keywords proceed charges
            re.DOTALL  # matches all chars, including newlines
        ),
        "clean_up": lambda x: x.replace("\n", "; "),
        "limit_size": 400,
    }, {
        "field": "bail",
        "pattern": re.compile(
            r"(Amount\n)"  # first find 'Amount' and newline
            r"\$"
            r"(?P<bail>(\d|,)*)"  # capture all digits and commas
            r"\.00",  # end with '.00'
            re.DOTALL
        ),
        "type_converter": lambda x: int(x),
        "clean_up": lambda x: x.replace(",", ""),
        "limit_size": 15,
    }, {
        "field": "arresting_agency",
        "pattern": re.compile(
            r"\n[A-Z]\s\d{4,}.*"  # OTN number, eg. U 725538-2
            r"\n(?P<arresting_agency>.*(Police|PSP|police|District "  # 
            # capture group
            r"Attorney|district attorney|Detectives|detectives).*)\n"
        ),
        "limit_size": 100,
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



def parser(text: str, *,
           field: str,
           pattern: Pattern[str],
           type_converter: Optional[Callable] = None,
           clean_up: Optional[Callable] = None,
           limit_size: Optional[int] = None,
           null_value: Optional[Union[str, int, bool, None]] = None
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

        # Type
        final_value = type_converter(final_value)

    except (AttributeError, ValueError) as e:
        logging.info(
            "Parsing failed or couldn't find target value - setting " "to None"
        )
        final_value = null_value

    logging.info(f"{field.upper()}, FINAL: {final_value}")
    return final_value
