import unittest
from unittest import mock
import dotenv
import os
import logging

# project modules
from logs.config.logging import logs_config
from locations import paths, dirs, root_dir, test_dir
from modules.move_s3 import copy_file_to_s3_bucket
from tests.modules.test_move_s3.helper import \
    check_file_exists_in_s3_bucket, delete_key_in_bucket

# LOGGING
logs_config(paths["logs_config_test"])

# ENV VARS
dotenv.load_dotenv(root_dir / ".dev.env")

# MOCK VARS
mock_dirs = {
    "payload_json": test_dir / "fixtures/payload_json/",
}

mock_paths = {
    "payload_json": mock_dirs["payload_json"] / "dockets.json",
}

# MOCK ENV VARS
# We load our .env file because we need key id and secret key values to
# access our bucket. However, we want to move our testing file into a
# different bucket and folder than defined in our .env
mock_env = os.environ
mock_env["BUCKET_NAME"] = "penn-playground"
mock_env["DESTINATION_PATH"] = "test_data/dockets.json"

class TestMoveS3(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        delete_key_in_bucket(mock_env["BUCKET_NAME"],
            mock_env["DESTINATION_PATH"])

    @mock.patch.dict(paths, mock_paths, clear=True)
    @mock.patch.dict(
        os.environ, mock_env, clear=True
    )
    def test_file_is_moved_to_s3_bucket(self):
        """
        Test that file is succesfully copied to s3 bucket
        """
        copy_file_to_s3_bucket()
        file_exists = check_file_exists_in_s3_bucket(mock_env["BUCKET_NAME"],
                                              mock_env["DESTINATION_PATH"])
        self.assertTrue(file_exists)




if __name__ == "__main__":
    unittest.main()
