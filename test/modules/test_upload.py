import unittest

# in-built or third party libs
import os
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
import pandas as pd
import requests

# modules to test
from modules.upload import upload_to_rest_api, login, logout


class TestUpload(unittest.TestCase):

    def setUp(self) -> None:

        """
        Loading rest config settings and dummy data
        """
        load_dotenv(find_dotenv())
        self.paths = {
            "payload_csv": Path("../fixtures/csv_payload/dockets.csv")  # dummy data
        }
        self.rest_api = {
            # "hostname": os.environ.get("REST_API_HOSTNAME"),
            "hostname": "http://localhost:5000",
            "login_endpoint": os.environ.get("LOGIN_END_POINT"),
            "logout_endpoint": os.environ.get("LOGOUT_END_POINT"),
            "post_endpoint": os.environ.get("POST_END_POINT"),
            "username": os.environ.get("REST_API_USERNAME"),
            "password": os.environ.get("REST_API_PASSWORD"),
        }
        df = pd.read_csv(self.paths["payload_csv"], dtype={"docketnum": str})
        self.list_of_docketnums_uploaded = df["docketnum"].to_list()

    def tearDown(self) -> None:
        """
        Deleting cases added to database
        """
        # START REQUEST SESSION
        s = requests.Session()
        # LOGIN
        s = login(s, self.rest_api)
        # DELETE
        for docketnum in self.list_of_docketnums_uploaded:
            delete_endpoint = self.rest_api["hostname"] + "/case/" + docketnum
            r = s.delete(delete_endpoint)
            status_code = r.status_code
            data = r.json() if r.content else None
            # failure
            if status_code != 200:  # not status 'ok'
                print(data)
                return
            # success
            print(f"Deleted {docketnum}")
        # LOGOUT
        logout(s, self.rest_api)


if __name__ == "__main__":
    unittest.main()
