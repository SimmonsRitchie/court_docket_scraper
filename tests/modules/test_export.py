import unittest
from unittest import mock
import pandas as pd
from shutil import rmtree
from pathlib import Path

# fixtures
from tests.fixtures.dict_list.docket_list import docket_list
from locations import paths, dirs

# modules to test
from modules.export import (
    convert_dict_into_df,
    convert_df_to_csv,
    save_html_county_payload,
    convert_df_to_html,
)

mock_dirs = {
    "payload_csv": Path("../output/csv_converted_from_df/"),
    "payload_email": Path("../output/payload_email/"),
    "email_template": dirs["email_template"],  # using actual directory
}

mock_paths = {
    "payload_csv": mock_dirs["payload_csv"] / "dockets.csv",
    "payload_email": mock_dirs["payload_email"] / "email.html",
}


class TestExport(unittest.TestCase):
    def test_convert_dict_into_df(self):
        """
        Test that result is a dataframe
        """

        df = convert_dict_into_df(docket_list, "Dauphin")
        self.assertIsInstance(df, pd.core.frame.DataFrame)

    def test_convert_empty_dict_into_df(self):
        """
        Test that result is a dataframe
        """
        empty_dict = {}
        df = convert_dict_into_df(empty_dict, "Dauphin")
        self.assertIsInstance(df, pd.core.frame.DataFrame)


class TestConvertDfToCsv(unittest.TestCase):
    def setUp(self) -> None:
        mock_dirs["payload_csv"].mkdir(parents=True, exist_ok=True)  # make directory
        self.df = convert_dict_into_df(docket_list, "Dauphin")  # make testing df

    def tearDown(self) -> None:
        print(f"Deleting temp folder: {mock_dirs['payload_csv']}")
        rmtree(mock_dirs["payload_csv"])

    @mock.patch.dict(paths, mock_paths, clear=True)
    def test_csv_file_is_created(self):
        """
        Test that a CSV file is generated
        """

        # convert df to csv
        convert_df_to_csv(self.df)
        # Check csv has been created
        self.assertTrue(mock_paths["payload_csv"].is_file())


class TestSaveHtmlPayload(unittest.TestCase):
    def setUp(self) -> None:
        mock_dirs["payload_email"].mkdir(parents=True, exist_ok=True)
        # create testing df
        df = convert_dict_into_df(docket_list, "Dauphin")
        self.styled_df = convert_df_to_html(df)

    def tearDown(self) -> None:
        print(f"Deleting temp folder: {mock_dirs['payload_email']}")
        rmtree(mock_dirs["payload_email"])

    @mock.patch.dict(paths, mock_paths, clear=True)
    def test_html_file_is_created(self):
        """
        Test that an HTML file is generated
        """
        save_html_county_payload("blah blah blah", self.styled_df)
        # Check html file has been created
        self.assertTrue(mock_paths["payload_email"].is_file())


if __name__ == "__main__":
    unittest.main()
