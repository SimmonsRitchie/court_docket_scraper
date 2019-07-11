
import unittest
import os
from datetime import datetime
from pathlib import Path
import json
from time import sleep

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


    def test_email_sends(self):
        """
        Test that email successfully sends without error
        """
        email_notification(self.dirs, self.paths, self.date_and_time_of_scrape, self.target_scrape_day, self.county_list)


    # def test_email_detects_homicide_in_caps(self):
    #     """
    #     Test that email includes "homicide" in mobile tease content and subject line when "HOMICIDE" is among charges in email payload
    #     """
    #     # Set different paths for input and output email
    #     self.paths["payload_email"] = self.dirs["payload_email"] / "email-homicide1.html"
    #     self.paths["email_final"] = self.dirs["email_final"] / "email-homicide1.html"
    #
    #     email_notification(self.dirs, self.paths,self.destination_email_addresses, self.sender_email_address,
    #                        self.sender_email_password, self.date_and_time_of_scrape, self.target_scrape_day, self.county_list)
    #
    # def test_email_detects_homicide_in_lowecase(self):
    #     """
    #     Test that email includes "homicide" in mobile tease content and subject line when "homicide" is among charges in email payload
    #     """
    #     # Set different paths for input and output email
    #     self.paths["payload_email"] = self.dirs["payload_email"] / "email-homicide2.html"
    #     self.paths["email_final"] = self.dirs["email_final"] / "email-homicide2.html"
    #
    #     email_notification(self.dirs, self.paths, self.destination_email_addresses, self.sender_email_address,
    #                        self.sender_email_password, self.date_and_time_of_scrape, self.target_scrape_day, self.county_list)
    #
    #
    # def test_email_detects_murder_in_mismatched_case(self):
    #     """
    #     Test that email includes "murder" in mobile tease content and subject line when "mUrDER" is among
    #     charges in email payload
    #     """
    #     # Set different paths for input and output email
    #     self.paths["payload_email"] = self.dirs["payload_email"] / "email-murder1.html"
    #     self.paths["email_final"] = self.dirs["email_final"] / "email-murder1.html"
    #
    #     email_notification(self.dirs, self.paths, self.destination_email_addresses, self.sender_email_address,
    #                        self.sender_email_password, self.date_and_time_of_scrape, self.target_scrape_day, self.county_list)
    #
    # def test_email_detects_murder_when_homicide_present(self):
    #     """
    #     Test that email gives priority to "murder" in mobile tease content and subject line when "murder" and
    #     "homicide" are among charges in email payload.
    #     """
    #     # Set different paths for input and output email
    #     self.paths["payload_email"] = self.dirs["payload_email"] / "email-murder-and-hom.html"
    #     self.paths["email_final"] = self.dirs["email_final"] / "email-murder-and-hom.html"
    #
    #     email_notification(self.dirs, self.paths, self.destination_email_addresses, self.sender_email_address,
    #                        self.sender_email_password, self.date_and_time_of_scrape, self.target_scrape_day, self.county_list)



if __name__ == "__main__":
    unittest.main()
