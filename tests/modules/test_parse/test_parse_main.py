import unittest
import pprint as pp
from dotenv import load_dotenv

# project modules
from modules.parse import parse_main
from locations import paths, root_dir, test_dir
from logs.config.logging import logs_config

# LOGGING
logs_config(paths["logs_config_test"])

# ENV
load_dotenv(root_dir / ".dev.env")

# MOCK VARS
mock_dirs = {"extracted_text": test_dir / "fixtures/extracted_text/"}


class TestParseMain(unittest.TestCase):

    def test_parse_main_runs_without_error(self):
        """
        Test that function runs without error.
        """

        # parse text
        parsed_dict = {}
        extracted_text_dir = mock_dirs["extracted_text"]
        list_text_files = list(extracted_text_dir.glob("*.txt"))
        for count, text_file_path in enumerate(list_text_files):
            docketnum = text_file_path.stem
            text = text_file_path.read_text()
            parsed_dict[docketnum] = parse_main(text)

        pp.pprint(parsed_dict)
        print(parsed_dict)
