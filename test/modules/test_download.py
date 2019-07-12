import unittest
from unittest import mock
from pathlib import Path
from shutil import rmtree
import os

# import mocks
from test.mocks.driver import initialize_test_driver

# modules to test
from modules.download import download_pdf
from modules.initialize import initialize_driver
from locations import test_dirs

mock_dirs = {
    "pdfs": Path("../output/pdfs/").resolve(),
}

class TestPdfDownload(unittest.TestCase):
    def setUp(self) -> None:
        self.driver = initialize_test_driver()
        # self.driver = initialize_driver()
        mock_dirs["pdfs"].mkdir(parents=True, exist_ok=True)  # make directory


    # def tearDown(self) -> None:
    #     rmtree(mock_dirs["pdfs"])

    @mock.patch.dict(test_dirs, mock_dirs, clear=True)
    def test_download_pdf(self):
        """
        Test that we can download a PDF and then rename file
        """
        # set vars
        url = "https://ujsportal.pacourts.us/DocketSheets/MDJReport.ashx?docketNumber=MJ-19301-CR-0000267-2019&dnh=Y8vjNGxZW%2fBPTn0Voa9E2g%3d%3d"
        docketnum = "MJ-19301-CR-0000267-2019"
        # download
        pdf_path = download_pdf(self.driver, url, docketnum)
        # assert
        self.assertTrue(pdf_path.is_file())
