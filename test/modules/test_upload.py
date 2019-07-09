import unittest

# in-built or third party libs
import os
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
# modules to test
from modules.upload import upload_to_rest_api

class TestInitialize(unittest.TestCase):
    def test_chrome_driver_initializes(self):
        """
        Test that data uploads to web service properly
        """
        load_dotenv(find_dotenv())
        paths = {
            "payload_csv": Path("../fixtures/csv_payload/dockets.csv") # dummy data
        }
        rest_api = {
            "hostname": os.environ.get("REST_API_HOSTNAME"),
            "login_endpoint": os.environ.get("LOGIN_END_POINT"),
            "logout_endpoint": os.environ.get("LOGOUT_END_POINT"),
            "post_endpoint": os.environ.get("POST_END_POINT"),
            "username": os.environ.get("REST_API_USERNAME"),
            "password": os.environ.get("REST_API_PASSWORD"),
        }
        upload_to_rest_api(rest_api, paths)





if __name__ == "__main__":
    unittest.main()
