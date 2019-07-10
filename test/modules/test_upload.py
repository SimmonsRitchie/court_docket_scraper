import unittest

# in-built or third party libs
import os
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
import pandas as pd
import requests

# modules to test
from modules.upload import upload_to_rest_api, login, logout

def helper_delete(s, rest_api, list_of_docketnums):
    """
    This helper function deletes data that has matching docketnums
    """

    for docketnum in list_of_docketnums:
        delete_endpoint = rest_api["hostname"] + "/case/" + docketnum
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
    print("Getting cases...")
    get_cases_endpoint = rest_api["hostname"] + "/cases"
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


class TestUpload(unittest.TestCase):

    def setUp(self) -> None:

        """
        Loading rest config settings and dummy data
        """
        # load_dotenv(find_dotenv())
        self.paths = {
            "payload_csv": Path("../fixtures/csv_payload/dockets.csv")  # dummy data
        }
        self.rest_api = {
            # "hostname": os.environ.get("REST_API_HOSTNAME"),
            "hostname": os.environ.get("REST_API_HOSTNAME"),
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
        print("TEARDOWN")
        # START REQUEST SESSION
        s = requests.Session()
        # LOGIN
        s = login(s, self.rest_api)
        # DELETE
        s = helper_delete(s, self.rest_api, self.list_of_docketnums_uploaded)
        # LOGOUT
        logout(s, self.rest_api)


    def test_upload_cases_to_db(self):
        """
        Test that data uploads to web service properly
        """
        # upload data
        upload_to_rest_api(self.rest_api, self.paths)

        # check data is uploaded
        list_of_dockets_in_db = helper_get_docketnums_in_db(self.rest_api)

        # asserts
        self.assertTrue(set(list_of_dockets_in_db).issubset(list_of_dockets_in_db))


if __name__ == "__main__":
    unittest.main()
