import unittest
from unittest import mock

# in-built or third party libs
import os
import pandas as pd
import requests

# modules to test
from modules.upload import upload_to_rest_api, login, logout
from locations import paths, root_dir, test_dir
from logs.config.logging import logs_config
from tests.modules.test_upload.helpers import helper_delete, helper_get_docketnums_in_db
# LOGGING
logs_config(paths["logs_config_test"])

# MOCK VARS
mock_paths = {"payload_csv": test_dir / "fixtures/payload_csv/dockets.csv"}
mock_env = os.environ
mock_env["ERROR_EMAILS"] = "FALSE"


class TestUpload(unittest.TestCase):
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
        df = pd.read_csv(mock_paths["payload_csv"], dtype={"docketnum": str})
        print(df)
        self.list_of_docketnums_to_be_uploaded = df["docketnum"].to_list()

    # def tearDown(self) -> None:
    #     """
    #     Deleting cases added to database
    #     """
    #     print("TEARDOWN")
    #     # START REQUEST SESSION
    #     s = requests.Session()
    #     try:
    #         # LOGIN
    #         s = login(s, self.rest_api)
    #         # DELETE
    #         s = helper_delete(s, self.rest_api, self.list_of_docketnums_to_be_uploaded)
    #         # LOGOUT
    #         logout(s, self.rest_api)
    #     except Exception as error:
    #         print(error)
    #     s.close()

    @mock.patch.dict(paths, mock_paths, clear=True)
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


if __name__ == "__main__":
    unittest.main()
