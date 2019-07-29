import unittest
from unittest import mock
from datetime import datetime, timedelta
from shutil import rmtree
import os
import json
import dotenv

# project modules
from logs.config.logging import logs_config
from locations import paths, dirs, root_dir, test_dir
from modules.email import email_notification

# LOGGING
logs_config(paths["logs_config_test"])

# ENV VARS
dotenv.load_dotenv(root_dir / ".dev.env")

# MOCK VARS
mock_dirs = {
    "payload_email": test_dir / "fixtures/payload_email/",
    "email_template": dirs["email_template"],
    "email_final": test_dir / "output/email_final/",
    "payload_csv": test_dir / "fixtures/payload_csv/",
}

mock_paths = {
    "payload_email": mock_dirs["payload_email"] / "email.html",
    "email_final": mock_dirs["email_final"] / "email.html",
    "payload_csv": mock_dirs["payload_csv"] / "dockets.csv",
}


class TestEmail(unittest.TestCase):
    def setUp(self) -> None:
        # clean up
        if mock_dirs["email_final"].is_dir():
            rmtree(mock_dirs["email_final"])
        mock_dirs["email_final"].mkdir(parents=True, exist_ok=True)

        # vars
        self.scrape_start_time = (datetime.now() - timedelta(hours=1.3))
        self.scrape_end_time = datetime.now()
        self.target_scrape_day = "today"
        self.county_list = ["Cumberland"]

    def tearDown(self) -> None:
        pass

    @mock.patch.dict(paths, mock_paths, clear=True)
    @mock.patch.dict(dirs, mock_dirs, clear=True)
    def test_email_sends(self):
        """
        Test that email successfully sends without error
        """
        email_notification(
            self.scrape_start_time,
            self.scrape_end_time,
            self.target_scrape_day,
            self.county_list
        )


if __name__ == "__main__":
    unittest.main()
