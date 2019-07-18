import logging
import unittest
from logs.config.logging import logs_config
from pathlib import Path
import pprint as pp

# project modules
from locations import paths
from modules.parse import parser, parser_recipe
from shutil import copyfile

# fixtures
test_dirs = {"extracted_text": Path("../../fixtures/extracted_text/")}


class TestParseBail(unittest.TestCase):
    # def setUp(self) -> None:
    #     logs_config(paths["logs_config_test"])

    def test_parsed_defendant_matches_expected_values(self):
        """
        Test that extracted bail matches expected values.
        """
        dict_to_match = {
            'MJ-02202-CR-0000202-2019': 'Charles Joseph Hargroves',
            'MJ-02205-CR-0000138-2019': 'Tiffany Shirley'
        }

        # parse text
        parsed_dict = {}
        bail_recipe = next((recipe for recipe in parser_recipe if recipe[
            'field'] == "defendant"), None)
        extracted_text_dir = test_dirs["extracted_text"]
        list_text_files = list(extracted_text_dir.glob("*.txt"))
        for count, text_file_path in enumerate(list_text_files):
            docketnum = text_file_path.stem
            text = text_file_path.read_text()
            parsed_dict[docketnum] = parser(text, **bail_recipe)

        # check that dict_to_match key-values are subset of parsed_dict
        self.assertTrue(dict_to_match.items() <= parsed_dict.items())
        pp.pprint(parsed_dict)
