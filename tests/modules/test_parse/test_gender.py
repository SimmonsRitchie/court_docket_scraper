import unittest
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
mock_dirs = {"extracted_text": test_dir / "fixtures/extracted_text_race/"}


class TestParseBail(unittest.TestCase):
    # def setUp(self) -> None:
    #     logs_config(paths["logs_config_test"])

    def test_parsed_defendant_matches_expected_values(self):
        """
        Test that extracted bail matches expected values.
        """
        dict_to_match = {
            "MJ-02101-CR-0000428-2019": "Malchom Morgan",
            "MJ-02101-CR-0000429-2019": "Megan Elizabeth Boyle",
        }

        # parse text
        parsed_dict = {}
        bail_recipe = next(
            (recipe for recipe in parser_recipe if recipe["field"] ==
             "defendant_gender"), None
        )
        extracted_text_dir = mock_dirs["extracted_text"]
        list_text_files = list(extracted_text_dir.glob("*.txt"))
        for count, text_file_path in enumerate(list_text_files):
            docketnum = text_file_path.stem
            text = text_file_path.read_text()
            parsed_dict[docketnum] = parser(text, **bail_recipe)

        # check that dict_to_match key-values are subset of parsed_dict
        pp.pprint(parsed_dict)
        # self.assertTrue(dict_to_match.items() <= parsed_dict.items())
