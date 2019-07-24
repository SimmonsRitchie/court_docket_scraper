import unittest
from unittest import mock
from datetime import datetime
from shutil import rmtree
import os
import json
import dotenv

# project modules
from logs.config.logging import logs_config
from locations import paths, dirs, root_dir, test_dir
from modules.email import email_notification, login_to_gmail_and_send

# LOGGING
logs_config(paths["logs_config_test"])

# ENV VARS
dotenv.load_dotenv(root_dir / ".dev.env")

# MOCK VARS
mock_dirs = {
    "payload_email": test_dir / "fixtures/payload_email/",
    "email_template": dirs["email_template"],
    "email_final": test_dir / "output/email_final/",
    "payload_csv": test_dir / "fixtures/payload_csv/"
}

mock_paths = {
    "payload_email": mock_dirs["payload_email"] / "email-homicide1.html",
    "email_final": mock_dirs["email_final"] / "email.html",
    "payload_csv": mock_dirs["payload_csv"] /
                   "dockets_murder_and_hom.csv",
}


class TestEmailHomicideAndMurder(unittest.TestCase):
    def setUp(self) -> None:
        # clean up
        if mock_dirs["email_final"].is_dir():
            rmtree(mock_dirs["email_final"])
        mock_dirs["email_final"].mkdir(parents=True, exist_ok=True)

        # vars
        self.date_and_time_of_scrape = datetime.now().replace(microsecond=0).isoformat()
        self.target_scrape_day = "yesterday"
        self.county_list = ["Cumberland", "Perry", "York", "Lancaster"]

    def tearDown(self) -> None:
        pass


    @mock.patch.dict(paths, mock_paths, clear=True)
    @mock.patch.dict(dirs, mock_dirs, clear=True)
    def test_email_with_homicide_and_murder_sends(self):
        """
        Test that email notification successfully detects that a homicide
        and murder is included in CSV payload and responds accordingly.
        """
        email_notification(
            self.date_and_time_of_scrape, self.target_scrape_day, self.county_list
        )


if __name__ == "__main__":
    unittest.main()
