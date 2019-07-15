from unittest import mock
from pathlib import Path

# modules to test
from modules.initialize import initialize_driver
from locations import dirs

mock_dirs = {
    "pdfs": Path("../output/pdfs/").resolve(),
}

@mock.patch.dict(dirs, mock_dirs, clear=True)
def initialize_test_driver():
    """ By mocking the directory paths we force webdriver to set test/output/pdfs as default download directory"""
    return initialize_driver()