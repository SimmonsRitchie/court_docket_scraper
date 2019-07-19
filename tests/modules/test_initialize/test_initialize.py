import unittest
from selenium import webdriver
import dotenv

# project modules
from modules.initialize import initialize_driver
from locations import paths, root_dir
from logs.config.logging import logs_config

# LOGGING
logs_config(paths["logs_config_test"])

# ENV VARS
dotenv.load_dotenv(root_dir / ".dev.env")


class TestInitialize(unittest.TestCase):
    def test_chrome_driver_initializes(self):
        """
        Test that chrome driver initializes
        """
        driver = initialize_driver()
        self.assertIsInstance(driver, webdriver.Chrome)
        driver.close()


if __name__ == "__main__":
    unittest.main()
