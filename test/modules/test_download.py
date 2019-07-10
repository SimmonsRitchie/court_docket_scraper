import unittest
from pathlib import Path
from shutil import rmtree
import os

# import fixtures

# modules to test
from modules.download import download_pdf
from modules.initialize import initialize_driver

class TestPdfDownload(unittest.TestCase):
    def setUp(self) -> None:
        chrome_driver_path = os.environ.get("CHROME_DRIVER_PATH")
        self.dirs = {
            "pdfs": Path("../output/pdfs/").resolve() # get absolute path to avoid issues with file location
        }
        self.driver = initialize_driver(self.dirs, chrome_driver_path)
        self.docketnum = "MJ-19301-CR-0000267-2019"
        self.url = "https://ujsportal.pacourts.us/DocketSheets/MDJReport.ashx?docketNumber=MJ-19301-CR-0000267-2019&dnh=Y8vjNGxZW%2fBPTn0Voa9E2g%3d%3d"
        self.expected_pdf_path = self.dirs["pdfs"] / f"{self.docketnum}.pdf"

    def tearDown(self) -> None:
        rmtree(self.dirs["pdfs"])

    def test_generate_unique_pdf_names(self):
        """
        Test that we can download a PDF and then rename file
        """
        pdf_path = download_pdf(self.driver, self.url, self.docketnum, self.dirs)
        self.assertTrue(pdf_path.is_file())

