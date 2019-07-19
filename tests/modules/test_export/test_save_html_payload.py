import unittest
from unittest import mock
import pandas as pd
from shutil import rmtree
from pathlib import Path

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
from locations import paths, dirs


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
        rmtree(mock_dirs["payload_email"])
        mock_dirs["payload_email"].mkdir(parents=True, exist_ok=True)
        # create testing df
        self.df = convert_dict_into_df(docket_list, "Dauphin")
        logs_config(paths["logs_config_test"])


    # def tearDown(self) -> None:
    #     print(f"Deleting temp folder: {mock_dirs['payload_email']}")
    #     rmtree(mock_dirs["payload_email"])

    @mock.patch.dict(paths, mock_paths, clear=True)
    def test_html_file_is_created(self):
        """
        Test that an HTML file is generated
        """
        styled_df = convert_df_to_html(self.df)
        save_html_county_payload("This is an introduction for the email",
                                 styled_df)
        # Check html file has been created
        self.assertTrue(mock_paths["payload_email"].is_file())


if __name__ == "__main__":
    unittest.main()
