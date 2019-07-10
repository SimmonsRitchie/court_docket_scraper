import unittest
import pandas as pd
import tempfile
import os
import shutil
from io import StringIO

# fixtures
from test.fixtures.dict_list.docket_list import docket_list

# modules to test
from modules.export import convert_dict_into_df, convert_df_to_csv, convert_df_to_html
from modules.misc import csv_payload_path_generator


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

    def test_convert_df_to_csv(self):
        """
        Test that file is generated
        """
        county = "Dauphin"
        # outfile_directory_path = tempfile.mkdtemp()
        outfile_directory_path = "../output_files/"
        df = convert_dict_into_df(docket_list, county)
        convert_df_to_csv(df, outfile_directory_path)
        outfile_full_path = csv_payload_path_generator(outfile_directory_path)
        with open(outfile_full_path, "r") as fin:
            contents = fin.read()
        # NOTE: To remove the tempfile add try-finally clause and shutil.rmtree(outfile_directory_path)

        self.assertTrue(contents)

    def test_convert_df_to_html(self):
        """
        Test that file is generated
        """


if __name__ == "__main__":
    unittest.main()
