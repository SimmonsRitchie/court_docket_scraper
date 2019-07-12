import unittest
from unittest import mock

# in-built or third party libs
import os
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
import pandas as pd
import requests

# modules to test
from modules.upload import upload_to_rest_api, login, logout
from locations import test_paths



def helper_delete(s, rest_api, list_of_docketnums):
    """
    This helper function deletes data that has matching docketnums
    """
    hostname = rest_api["hostname"]

    for docketnum in list_of_docketnums:
        delete_endpoint = hostname + "/case/" + docketnum
        r = s.delete(delete_endpoint)
        status_code = r.status_code
        data = r.json() if r.content else None
        # failure
        if status_code != 200:  # not status 'ok'
            print(data)
            return
        # success
        print(f">> Deleted {docketnum}")
    print("All cases deleted")
    return s


def helper_get_docketnums_in_db(rest_api):
    """
    This helper function returns a list of all docketnums in our db
    """

    hostname = rest_api["hostname"]

    print("Getting cases...")
    get_cases_endpoint = hostname + "/cases"
    r = requests.get(get_cases_endpoint)
    status_code = r.status_code
    data = r.json()
    # failure
    if status_code != 200:  # not status 'ok'
        print(data)
        return
    # success
    cases = data["cases"]
    return [case["docketnum"] for case in cases]


mock_paths = {
    "payload_csv": Path("../fixtures/payload_csv/dockets.csv")  # dummy data
}

class TestUpload(unittest.TestCase):
    def setUp(self) -> None:

        """
        Loading rest config settings and dummy data
        """
        df = pd.read_csv(mock_paths["payload_csv"], dtype={"docketnum": str})
        self.list_of_docketnums_that_should_be_uploaded = df["docketnum"].to_list()

        self.rest_api = {
            "hostname": os.getenv("REST_API_HOSTNAME"),
            "login_endpoint": os.getenv("LOGIN_END_POINT"),
            "logout_endpoint": os.getenv("LOGOUT_END_POINT"),
            "post_endpoint": os.getenv("POST_END_POINT"),
            "username": os.getenv("REST_API_USERNAME"),
            "password": os.getenv("REST_API_PASSWORD"),
        }

    def tearDown(self) -> None:
        """
        Deleting cases added to database
        """
        print("TEARDOWN")
        # START REQUEST SESSION
        s = requests.Session()
        try:
            # LOGIN
            s = login(s, self.rest_api)
            # DELETE
            s = helper_delete(s, self.rest_api, self.list_of_docketnums_that_should_be_uploaded)
            # LOGOUT
            logout(s, self.rest_api)
        except Exception as error:
            print(error)

    @mock.patch.dict(test_paths, mock_paths, clear=True)
    def test_upload_cases_to_db(self):
        """
        Test that data uploads to web service properly
        """
        # upload data
        upload_to_rest_api()

        # check all docket nums are in db
        list_of_dockets_in_db = []
        try:
            list_of_dockets_in_db = helper_get_docketnums_in_db(self.rest_api)
        except Exception as error:
            print(error)
        test_bool = all(
            elem in list_of_dockets_in_db for elem in self.list_of_docketnums_that_should_be_uploaded
        )

        # asserts
        self.assertTrue(test_bool)


if __name__ == "__main__":
    unittest.main()
