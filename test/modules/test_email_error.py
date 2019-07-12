
import unittest
import os
from datetime import datetime
from pathlib import Path
import json
from time import sleep
from unittest import mock


# modules to test
from modules.email import email_error_notification
from locations import test_dirs, mock_dirs

class TestEmailError(unittest.TestCase):

    def setUp(self) -> None:
        # vars
        self.dirs = {
            "email_template": Path("../../static/email_template/"),
            "email_error": Path("../output/email_error/"),
        }

        self.paths = {
            "email_error": self.dirs["email_error"] / "email.html",
        }

        # build temp directory
        self.dirs["email_error"].mkdir(parents=True, exist_ok=True) # generate a subdirectory for testing purposes


    def tearDown(self) -> None:
        sleep(0.2) # wait a second between sending emails, so Gmail doesn't freak out

    def test_error_email_runs_without_errors(self):
        """
        Test that email successfully sends without error
        """
        error_summary = "Error when uploading data to database"
        full_error_msg = "HTTPConnectionPool(host='localhost', port=5000): Max retries exceeded with url: /cases (" \
                       "Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x1051665f8>: Failed to establish a new connection: [Errno 61] Connection refused'))"
        email_error_notification(error_summary, full_error_msg)
