import unittest
import os
from pathlib import Path

# project modules
from modules.initialize import initialize_driver
from modules.misc import yesterday_date
from logs.config.logging import logs_config
from modules.scrape import scrape_search_results
import logging
from locations import paths

class TestScrape(unittest.TestCase):
    def setUp(self) -> None:
        self.driver = initialize_driver()
        logs_config(paths["logs_config_test"])

    def test_scrape_without_error(self):
        """
        Test that a single county's docket's for yesterday's date can be scraped without raising an error.
        """
        scrape_date = yesterday_date() # get string of yesterday's date
        docket_list = scrape_search_results(self.driver, "Dauphin", scrape_date)
        logging.info(docket_list)


if __name__ == "__main__":
    unittest.main()