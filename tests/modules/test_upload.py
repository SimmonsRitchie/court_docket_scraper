import unittest
from unittest import mock

# in-built or third party libs
import os
from pathlib import Path
import pandas as pd
import requests

# modules to test
from modules.upload import upload_to_rest_api, login, logout
from locations import paths


# Path to normal CSV payload data
mock_paths1 = {"payload_csv": Path("../fixtures/payload_csv/dockets.csv")}  # dummy data
# Path to bad CSV payload data that has a string in bail field
mock_paths2 = {"payload_csv": Path("../fixtures/payload_csv/dockets_bad1.csv")}

# we set this to prevent error emails from sending during upload failure
mock_env = os.environ
mock_env["ERROR_EMAILS"] = "FALSE"


def helper_delete(s, rest_api, list_of_docketnums):
    """
    This helper function deletes data that has matching docketnums
    """
    hostname = rest_api["hostname"]
    delete_count = 0
    for docketnum in list_of_docketnums:
        delete_endpoint = hostname + "/case/" + docketnum
        r = s.delete(delete_endpoint)
        status_code = r.status_code
        data = r.json() if r.content else None
        # failure
        if status_code != 200:  # not status 'ok'
            print(data)
        else:
            # success
            print(f">> Deleted {docketnum}")
            delete_count += 1
    print(f"{delete_count} cases deleted")
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


class TestUpload1(unittest.TestCase):
    def setUp(self) -> None:

        """
        Loading rest config settings and dummy data
        """
        self.rest_api = {
            "hostname": os.getenv("REST_API_HOSTNAME"),
            "login_endpoint": os.getenv("LOGIN_END_POINT"),
            "logout_endpoint": os.getenv("LOGOUT_END_POINT"),
            "post_endpoint": os.getenv("POST_END_POINT"),
            "username": os.getenv("REST_API_USERNAME"),
            "password": os.getenv("REST_API_PASSWORD"),
        }

        # get expected data
        df = pd.read_csv(mock_paths1["payload_csv"], dtype={"docketnum": str})
        self.list_of_docketnums_to_be_uploaded = df["docketnum"].to_list()

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
            s = helper_delete(s, self.rest_api, self.list_of_docketnums_to_be_uploaded)
            # LOGOUT
            logout(s, self.rest_api)
        except Exception as error:
            print(error)
        s.close()

    @mock.patch.dict(paths, mock_paths1, clear=True)
    @mock.patch.dict(
        os.environ, mock_env, clear=True
    )  # to prevent error emails from sending
    def test_upload_cases_to_db(self):
        """
        Test that data successfully uploads to web service
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
            elem in list_of_dockets_in_db
            for elem in self.list_of_docketnums_to_be_uploaded
        )

        # asserts
        self.assertTrue(test_bool)


class TestUpload2(unittest.TestCase):
    def setUp(self) -> None:

        """
        Loading rest config settings and dummy data
        """
        self.rest_api = {
            "hostname": os.getenv("REST_API_HOSTNAME"),
            "login_endpoint": os.getenv("LOGIN_END_POINT"),
            "logout_endpoint": os.getenv("LOGOUT_END_POINT"),
            "post_endpoint": os.getenv("POST_END_POINT"),
            "username": os.getenv("REST_API_USERNAME"),
            "password": os.getenv("REST_API_PASSWORD"),
        }

        # get expected data
        df = pd.read_csv(mock_paths2["payload_csv"], dtype={"docketnum": str})
        self.list_of_docketnums_to_be_uploaded = df["docketnum"].to_list()

    def tearDown(self) -> None:
        """
        Deleting cases added to database
        """
        print("TEARDOWN")
        # START REQUEST SESSION
        with requests.Session() as s:
            try:
                # LOGIN
                s = login(s, self.rest_api)
                # DELETE
                s = helper_delete(
                    s, self.rest_api, self.list_of_docketnums_to_be_uploaded
                )
                # LOGOUT
                logout(s, self.rest_api)
            except Exception as error:
                print(error)

    @mock.patch.dict(paths, mock_paths2, clear=True)
    @mock.patch.dict(
        os.environ, mock_env, clear=True
    )  # to prevent error emails from sending
    def test_bad_data_not_uploaded_to_db(self):
        """
        Test that bad data isn't uploaded to web service
        """
        # upload data
        upload_to_rest_api()

        # check NONE of the docket nums are in db
        list_of_dockets_in_db = []
        try:
            list_of_dockets_in_db = helper_get_docketnums_in_db(self.rest_api)
        except Exception as error:
            print(error)

        # asserts
        test_bool = not set(list_of_dockets_in_db).isdisjoint(
            self.list_of_docketnums_to_be_uploaded
        )
        self.assertFalse(test_bool)


if __name__ == "__main__":
    unittest.main()
