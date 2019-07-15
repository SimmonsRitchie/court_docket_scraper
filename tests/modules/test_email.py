
import unittest
from unittest import mock
import os
from datetime import datetime
from pathlib import Path
import json
from time import sleep
from shutil import rmtree

# modules to mock
from locations import paths, mock_paths, dirs, mock_dirs
# from mock_locations import mock_paths1

# modules to test
from modules.email import email_notification

mock_dirs = {
    "payload_email": Path("../fixtures/payload_email"),
    "email_template": dirs['email_template'],
    "email_final": Path("../output/email_final")
}

mock_paths = {
    "payload_email": mock_dirs["payload_email"] / "email.html",
    "email_final": mock_dirs["email_final"] / "email.html",
}

class TestEmail(unittest.TestCase):

    def setUp(self) -> None:
        # vars
        self.date_and_time_of_scrape = datetime.now().replace(microsecond=0).isoformat()
        self.target_scrape_day = "yesterday"
        self.county_list = ["Cumberland","Perry","York","Lancaster"]
        # build temp directory
        mock_dirs["email_final"].mkdir(parents=True, exist_ok=True)


    def tearDown(self) -> None:
        rmtree(mock_dirs["email_final"])

    @mock.patch.dict(paths, mock_paths, clear=True)
    @mock.patch.dict(dirs, mock_dirs, clear=True)
    def test_email_sends(self):
        """
        Test that email successfully sends without error
        """
        email_notification(self.date_and_time_of_scrape, self.target_scrape_day, self.county_list)


if __name__ == "__main__":
    unittest.main()
