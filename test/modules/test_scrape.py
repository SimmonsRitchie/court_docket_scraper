import unittest
import os
from pathlib import Path
from modules.initialize import initialize_driver
from modules.misc import yesterday_date

# modules to test
from modules.scrape import scrape_search_results

class TestScrape(unittest.TestCase):
    def setUp(self) -> None:
        base_folder_pdfs = Path("pdfs/")
        chrome_driver_path = os.environ.get("CHROME_DRIVER_PATH")
        self.driver = initialize_driver(base_folder_pdfs, chrome_driver_path)
        self.url = "https://ujsportal.pacourts.us/DocketSheets/MDJ.aspx"
        self.scrape_date = yesterday_date()

    def test_scrape_without_error(self):
        """
        Test that a single county's docket's for yesterday can be scraped without raising an error.
        """

        scrape_search_results(self.driver, self.url, self.county, self.scrape_date)


if __name__ == "__main__":
    unittest.main()
