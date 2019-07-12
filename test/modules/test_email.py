
import unittest
from unittest import mock
import os
from datetime import datetime
from pathlib import Path
import json
from time import sleep

# modules to mock
from locations import test_paths, mock_paths, test_dirs, mock_dirs
# from mock_locations import mock_paths

# modules to test
from modules.email import email_notification

class TestEmail(unittest.TestCase):

    def setUp(self) -> None:
        # vars
        self.dirs = {
            "payload_email": Path("../fixtures/payload_email/"),
            "email_final": Path("../output/email_final/"),
            "email_template": Path("../../static/email_template/"),
        }

        self.paths = {
            "payload_email": (self.dirs["payload_email"] / "email.html"),
            "email_final": self.dirs["email_final"] / "email.html",
        }
        self.date_and_time_of_scrape = datetime.now().replace(microsecond=0).isoformat()

        # environ vars
        self.target_scrape_day = "yesterday"
        self.county_list = ["Cumberland","Perry","York","Lancaster"]

        # build temp directory
        self.dirs["email_final"].mkdir(parents=True, exist_ok=True) # generate a subdirectory for testing purposes


    def tearDown(self) -> None:
        sleep(0.2) # wait a second between sending emails, so Gmail doesn't freak out


    @mock.patch.dict(test_paths, mock_paths, clear=True)
    @mock.patch.dict(test_dirs, mock_dirs, clear=True)
    def test_email_sends(self):
        """
        Test that email successfully sends without error
        """
        email_notification(self.date_and_time_of_scrape, self.target_scrape_day, self.county_list)


if __name__ == "__main__":
    unittest.main()
