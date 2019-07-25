import unittest
from unittest import mock
from pathlib import Path
from shutil import rmtree
from dotenv import load_dotenv

# project modules
from modules.download import download_pdf
from modules.initialize import initialize_driver
from locations import dirs, paths, root_dir, test_dir
from logs.config.logging import logs_config

# LOGGING
logs_config(paths["logs_config_test"])

# ENV
load_dotenv(root_dir / ".dev.env")

# MOCK VARS
mock_dirs = {
    "pdfs": test_dir / "output/pdfs"
}  # NOTE: Must have resolve otherwise you'll have problems

# MOCK FUNCS
@mock.patch.dict(dirs, mock_dirs, clear=True)
def initialize_test_driver():
    """ By mocking the directory paths we force webdriver to set
    test/output/pdfs as default download directory """
    return initialize_driver()


# TESTS
class TestPdfDownload(unittest.TestCase):
    def setUp(self) -> None:
        # create clean output folder
        if mock_dirs["pdfs"].is_dir():
            rmtree(mock_dirs["pdfs"])
        mock_dirs["pdfs"].mkdir(parents=True, exist_ok=True)
        # init driver
        self.driver = initialize_test_driver()

    def tearDown(self) -> None:
        pass

    @mock.patch.dict(dirs, mock_dirs, clear=True)
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

    @mock.patch.dict(dirs, mock_dirs, clear=True)
    def test_error_raised_when_pdf_download_fails(self):
        """
        Test that we can download a PDF and then rename file
        """
        # set vars
        url = "https://ujsportal.pacourts.us/DocketSheets/MDJReport.ashx?docketNumber=INVALIDDOCKETURL"
        docketnum = "MJ-19301-CR-0000267-2019-FAKEDOCKET"
        # # download
        # pdf_path = download_pdf(self.driver, url, docketnum)
        # assert
        self.assertRaises(Exception, lambda: download_pdf(self.driver, url, docketnum))
        # self.assertFalse(pdf_path.is_file())
