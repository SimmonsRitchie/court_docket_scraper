import unittest
import pandas as pd
import tempfile
import os
import shutil
from io import StringIO
# fixtures
from test.fixtures.dict_list.docket_list import docket_list
# modules to test
from modules.export import convert_dict_into_df, convert_df_to_csv
from modules.misc import csv_payload_path_generator

class TestExport(unittest.TestCase):

    def test_convert_dict_into_df(self):
        """
        Test that result is a dataframe
        """

        df = convert_dict_into_df(docket_list, "Dauphin")
        self.assertIsInstance(df,pd.core.frame.DataFrame)

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




if __name__ == '__main__':
    unittest.main()

"""

UNITTEST: CHEAT SHEET

Running a single test case or test method:

    In parent folder type: python -m unittest test.test_search.TestSum

Running a single test module:

    In parent folder type: python -m unittest test.test_search

Run all tests:

    python -m unittest discover

UNITTEST - ASSERTION - API

assertEqual(a, b)
a == b

assertNotEqual(a, b)
a != b

assertTrue(x)
bool(x) is True

assertFalse(x)
bool(x) is False

assertIs(a, b)
a is b

assertIsNot(a, b)
a is not b

assertIsNone(x)
x is None

assertIsNotNone(x)
x is not None

assertIn(a, b)
a in b

assertNotIn(a, b)
a not in b

assertIsInstance(a, b)
isinstance(a, b)

assertNotIsInstance(a, b)
not isinstance(a, b)

"""