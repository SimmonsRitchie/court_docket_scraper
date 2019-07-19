import unittest
from unittest import mock
import pandas as pd
from shutil import rmtree
from pathlib import Path
import logging

# fixtures
from tests.fixtures.dict_list.docket_list import docket_list

# project modules
from modules.export import (
    convert_dict_into_df,
    convert_df_to_csv,
    save_html_county_payload,
    convert_df_to_html,
)
from logs.config.logging import logs_config
from locations import paths, dirs, root_dir


mock_dirs = {
    "payload_csv": Path("../../output/csv_converted_from_df/"),
    "payload_email": Path("../../output/payload_email/"),
    "email_template": dirs["email_template"],  # using actual directory
}

mock_paths = {
    "payload_csv": mock_dirs["payload_csv"] / "dockets.csv",
    "payload_email": mock_dirs["payload_email"] / "email.html",
}


class TestSaveHtmlPayload(unittest.TestCase):
    def setUp(self) -> None:
        # start logging
        logs_config(paths["logs_config_test"])
        # delete previous test output files
        logging.info(f"Deleting {mock_dirs['payload_email']} if it exists")
        rmtree(mock_dirs["payload_email"])
        # rebuild directory
        mock_dirs["payload_email"].mkdir(parents=True, exist_ok=True)
        # create testing df
        # self.df = convert_dict_into_df(docket_list, "Dauphin")

        # SET PANDAS OPTIONS FOR PRINT DISPLAY
        pd.set_option("display.max_columns", 20)
        pd.set_option("display.width", 2000)
        pd.set_option("display.max_rows", 700)
        # # create testing df from problematic csv
        # self.df = pd.read_csv(
        # root_dir / "tests/fixtures/payload_csv/harrisburg_error.csv")

        # GET PROBLEMATIC DF
        self.df = pd.read_pickle(root_dir / "tests/fixtures/df_pkl/df.pkl")

    # def tearDown(self) -> None:
    #     print(f"Deleting temp folder: {mock_dirs['payload_email']}")
    #     rmtree(mock_dirs["payload_email"])

    @mock.patch.dict(paths, mock_paths, clear=True)
    def test_html_file_is_created(self):
        """
        Test that an HTML file is generated
        """
        styled_df = convert_df_to_html(self.df)
        # save_html_county_payload("This is an introduction for the email",
        #                          styled_df)
        # # Check html file has been created
        # self.assertTrue(mock_paths["payload_email"].is_file())


if __name__ == "__main__":
    unittest.main()
