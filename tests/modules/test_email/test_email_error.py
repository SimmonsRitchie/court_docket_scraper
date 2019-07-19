import unittest
import os
from datetime import datetime
from pathlib import Path
import json
from time import sleep
from unittest import mock
from logs.config.logging import logs_config


# modules to test
from modules.email import email_error_notification
from locations import paths


class TestEmailError(unittest.TestCase):
    def setUp(self) -> None:
        logs_config(paths["logs_config_test"])

    def tearDown(self) -> None:
        pass

    def test_error_email_runs_without_errors(self):
        """
        Test that email successfully sends without error
        """
        error_summary = "Error when uploading data to database"
        full_error_msg = (
            "HTTPConnectionPool(host='localhost', port=5000): Max retries exceeded with url: /cases ("
            "Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x1051665f8>: Failed to establish a new connection: [Errno 61] Connection refused'))"
        )
        email_error_notification(error_summary, full_error_msg)
