import logging
import unittest
from logs.config.logging import logs_config
from pathlib import Path

# project modules
from locations import paths
from modules.parse import parse_main

# fixtures
test_dirs = {
    "extracted_text": Path("../../fixtures/extracted_text/")
}

class TestCleanList(unittest.TestCase):
    def setUp(self) -> None:
        logs_config(paths["logs_config_test"])


    def test_text_is_parsed_without_error(self):
        """
        Test that extracted text files are parsed without causing an error.
        """
        extracted_text_dir = test_dirs["extracted_text"]
        list_text_files = list(extracted_text_dir.glob("*.txt"))  # we get all files with this suffix
        for count, text_file in enumerate(list_text_files):
            print(f"\n\nITEM {count}")
            text = text_file.read_text()
            parsed_data = parse_main(text)
            print(parsed_data)



