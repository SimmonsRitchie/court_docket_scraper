
import unittest
import os
from datetime import datetime
from pathlib import Path
import json

# fixtures
# from test.dirs import dirs, paths

# modules to test
from modules.email import email_notification


class TestEmail(unittest.TestCase):

    def setUp(self) -> None:
        # vars
        self.dirs = {
            "payload_email": Path("../fixtures/payload_email/"),
            "payload_csv": Path("../fixtures/csv_payload"),
            "email_final": Path("../output/email_final"),
            "email_template": Path("../../static/email_template"),
        }

        self.paths = {
            "payload_email": (self.dirs["payload_email"] / "email.html").resolve(),
            "payload_csv": self.dirs["payload_csv"] / "dockets.csv",
            "email_final": self.dirs["email_final"] / "email.html",
        }
        self.date_and_time_of_scrape = datetime.now().replace(microsecond=0).isoformat()

        # environ vars
        self.destination_email_addresses = json.loads(
        os.environ.get("DESTINATION_EMAIL_ADDRESSES")
    )
        self.sender_email_address = os.environ.get("SENDER_EMAIL_USERNAME")
        self.sender_email_password = os.environ.get("SENDER_EMAIL_PASSWORD")
        self.target_scrape_day = "yesterday"
        self.county_list = ["Cumberland","Perry","York","Lancaster"]

        # build temp directory
        self.dirs["email_final"].mkdir(parents=True, exist_ok=True) # generate a subdirectory for testing purposes

    # def tearDown(self) -> None:
    #     rmtree(self.dir)

    def test_email_sends(self):
        """
        Email successfully sends without error
        """
        email_notification(self.dirs, self.paths,self.destination_email_addresses, self.sender_email_address,
                           self.sender_email_password, self.date_and_time_of_scrape, self.target_scrape_day, self.county_list)




if __name__ == "__main__":
    unittest.main()
