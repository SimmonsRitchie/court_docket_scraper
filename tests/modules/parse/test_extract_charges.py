import logging
import unittest
from logs.config.logging import logs_config
from pathlib import Path
import pprint as pp

# project modules
from locations import paths
from modules.parse import extract_charges

# fixtures
test_dirs = {"extracted_text": Path("../../fixtures/extracted_text/")}


class TestParseCharges(unittest.TestCase):
    # def setUp(self) -> None:
    # logs_config(paths["logs_config_test"])

    def test_parsed_charges_match_expected_values(self):
        """
        Test that extracted bail matches expected values.
        """
        dict_to_match = {
            "MJ-12305-CR-0000211-2019": "Theft By Unlaw Taking-Movable Prop; Receiving Stolen Property",
            "MJ-12304-CR-0000259-2019": "Resist Arrest/Other Law Enforce; "
            "Int Poss Contr Subst By Per Not Reg; Marijuana-Small Amt Personal Use; Use/Poss Of Drug Paraph",
            "MJ-12301-CR-0000163-2019": "Endangering Welfare of Children - ; Parent/Guardian/Other Commits Offense;"
            " DUI: Controlled Substance - Schedule 2 or 3 - 1st ; Offense; DUI: Controlled"
            " Substance - Impaired Ability - 1st ; Offense; Endangering Welfare of Children"
            " - ; Parent/Guardian/Other Commits Offense; Driving W/O A License",
        }

        # parse text
        parsed_dict = {}
        extracted_text_dir = test_dirs["extracted_text"]
        list_text_files = list(extracted_text_dir.glob("*.txt"))
        for count, text_file_path in enumerate(list_text_files):
            docketnum = text_file_path.stem
            text = text_file_path.read_text()
            parsed_dict[docketnum] = extract_charges(text)

        # check that dict_to_match key-values are subset of parsed_dict
        self.assertTrue(dict_to_match.items() <= parsed_dict.items())
        print(parsed_dict)
