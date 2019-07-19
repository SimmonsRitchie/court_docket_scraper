import logging
import unittest
from logs.config.logging import logs_config
from pathlib import Path
import pprint as pp

# project modules
from locations import paths
from modules.parse import parse_main

# fixtures
test_dirs = {"extracted_text": Path("../../fixtures/extracted_text/")}


class TestParseMain(unittest.TestCase):
    # def setUp(self) -> None:
    #     logs_config(paths["logs_config_test"])

    def test_parse_main_runs_without_error(self):
        """
        Test that function runs without error.
        """

        # parse text
        parsed_dict = {}
        extracted_text_dir = test_dirs["extracted_text"]
        list_text_files = list(extracted_text_dir.glob("*.txt"))
        for count, text_file_path in enumerate(list_text_files):
            docketnum = text_file_path.stem
            text = text_file_path.read_text()
            parsed_dict[docketnum] = parse_main(text)

        pp.pprint(parsed_dict)
