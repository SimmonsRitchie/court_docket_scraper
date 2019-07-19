import unittest
from unittest import mock
from datetime import datetime
from pathlib import Path
from shutil import rmtree
import os
import json
import dotenv

# modules to mock
from locations import paths, dirs, root_dir

# modules to test
from modules.email import email_notification, login_to_gmail_and_send

mock_dirs = {
    "payload_email": Path("../../fixtures/payload_email"),
    "email_template": dirs["email_template"],
    "email_final": Path("../../output/email_final"),
    "payload_csv": Path("../../fixtures/payload_csv"),
}

mock_paths = {
    "payload_email": mock_dirs["payload_email"] / "email.html",
    "email_final": mock_dirs["email_final"] / "email.html",
    "payload_csv": mock_dirs["payload_csv"] / "dockets.csv",
}

# Load ENV vars
dotenv.load_dotenv(root_dir / ".dev.env")


class TestEmail(unittest.TestCase):
    def setUp(self) -> None:
        # vars
        self.date_and_time_of_scrape = datetime.now().replace(microsecond=0).isoformat()
        self.target_scrape_day = "yesterday"
        self.county_list = ["Cumberland", "Perry", "York", "Lancaster"]
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
        email_notification(
            self.date_and_time_of_scrape, self.target_scrape_day, self.county_list
        )

    @mock.patch.dict(paths, mock_paths, clear=True)
    @mock.patch.dict(dirs, mock_dirs, clear=True)
    def test_email_with_attachments_sends(self):
        """
        Test that email with attachments successfully sends without error
        """
        email_args = {
            "recipients": json.loads(os.getenv("DESTINATION_EMAIL_ADDRESSES")),
            "html_msg": "<p>This is a test to see that an email with attachments can be sent without error.</p>",
            "subject_line": "this is a test - with attachments",
            "attachments": [mock_paths["payload_csv"]],
        }
        login_to_gmail_and_send(**email_args)


if __name__ == "__main__":
    unittest.main()
