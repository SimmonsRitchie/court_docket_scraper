import logging
import unittest
from logs.config.logging import logs_config
from pathlib import Path
import pprint as pp
from dotenv import load_dotenv

# project modules
from modules.parse import parser_recipe, parser
from locations import paths, root_dir, test_dir
from logs.config.logging import logs_config

# LOGGING
logs_config(paths["logs_config_test"])

# ENV
load_dotenv(root_dir / ".dev.env")

# MOCK VARS
mock_dirs = {"extracted_text": test_dir /
                               "fixtures/extracted_text_bail_difficult/"}


class TestParseBail(unittest.TestCase):


    def test_parsed_bail_matches_expected_values(self):
        """
        Test that extracted bail matches expected values.
        """
        dict_to_match = {
            "MJ-12104-CR-0000480-2019": 1
        }

        # parse text
        parsed_dict = {}
        bail_recipe = next(
            (recipe for recipe in parser_recipe if recipe["field"] == "bail"), None
        )
        extracted_text_dir = mock_dirs["extracted_text"]
        list_text_files = list(extracted_text_dir.glob("*.txt"))
        for count, text_file_path in enumerate(list_text_files):
            docketnum = text_file_path.stem
            text = text_file_path.read_text()
            parsed_dict[docketnum] = parser(text, **bail_recipe)

        # check that dict_to_match key-values are subset of parsed_dict
        pp.pprint(parsed_dict)
        self.assertTrue(dict_to_match.items() <= parsed_dict.items())
