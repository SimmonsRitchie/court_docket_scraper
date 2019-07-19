import unittest
from dotenv import load_dotenv

# project modules
from modules.initialize import initialize_driver
from modules.misc import yesterday_date
from modules.scrape import scrape
from locations import paths, root_dir
from logs.config.logging import logs_config
import logging

# LOGGING
logs_config(paths["logs_config_test"])

# ENV
load_dotenv(root_dir / ".dev.env")


class TestScrape(unittest.TestCase):
    def setUp(self) -> None:
        self.driver = initialize_driver()

    def test_scrape_without_error(self):
        """
        Test that a single county's docket's for yesterday's date can be scraped without raising an error.
        """
        scrape_date = yesterday_date()  # get string of yesterday's date
        docket_list = scrape("Dauphin", scrape_date)
        logging.info(docket_list)


if __name__ == "__main__":
    unittest.main()
