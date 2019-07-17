import unittest

# in-built or third party libs
from selenium import webdriver


# modules to test
from modules.initialize import initialize_driver

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
