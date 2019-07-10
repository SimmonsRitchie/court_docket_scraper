import unittest

# in-built or third party libs
import os
from selenium import webdriver
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

# modules to test
from modules.initialize import initialize_driver


class TestInitialize(unittest.TestCase):
    def test_chrome_driver_initializes(self):
        """
        Test that chrome driver initializes
        """
        dirs = {
            "pdfs": Path("../output_files/pdfs/")
        }
        load_dotenv(find_dotenv())
        chrome_driver_path = os.environ.get("CHROME_DRIVER_PATH")
        print(chrome_driver_path)

        driver = initialize_driver(dirs, chrome_driver_path)
        self.assertIsInstance(driver, webdriver.Chrome)
        driver.close()


if __name__ == "__main__":
    unittest.main()
