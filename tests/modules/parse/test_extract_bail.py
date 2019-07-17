import logging
import unittest
from logs.config.logging import logs_config
from pathlib import Path
import pprint as pp
# project modules
from locations import paths
from modules.parse import extract_bail
from shutil import copyfile

# fixtures
test_dirs = {
    "extracted_text": Path("../../fixtures/extracted_text/")
}

class TestParseBail(unittest.TestCase):
    # def setUp(self) -> None:
    #     logs_config(paths["logs_config_test"])

    def test_text_is_parsed_without_error(self):
        """
        Test that extracted text files are parsed without causing an error.
        """
        parsed_dict = {}
        extracted_text_dir = test_dirs["extracted_text"]
        list_text_files = list(extracted_text_dir.glob("*.txt"))
        for count, text_file_path in enumerate(list_text_files):
            docketnum = text_file_path.stem
            text = text_file_path.read_text()
            parsed_dict[docketnum] = extract_bail(text)
        pp.pprint(parsed_dict)




