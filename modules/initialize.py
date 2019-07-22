"""
This module initializes Chrome Driver in headless mode.

It also includes a hacky workaround to ensure that Chrome driver will download PDFs in headless mode. This is due to a
bug in Selenium/ChromeDriver. Note: I don't use Requests library to download PDFs because changes to USJ website meant
that it no longer worked.
"""

# Load selenium modules
from selenium import webdriver
import os
import logging
from pathlib import Path

# project modules
from locations import dirs


def initialize_driver() -> webdriver:

    logging.info("Initializing Chrome")

    # SET DRIVER PATH
    chrome_driver_path = Path(os.environ.get("CHROME_DRIVER_PATH"))
    logging.info(f"Chromedriver.exe location: {chrome_driver_path}")
    if not chrome_driver_path.is_file():
        logging.error("Chromedriver path doesn't exist")
        raise

    # SET DOWNLOAD PATH
    download_path = str(dirs["pdfs"])  # must be string, not Path instance
    logging.info(f"Driver download directory: {download_path}")
    logging.info("All files will be downloaded to this path")

    # Chrome options + initialize
    options = webdriver.ChromeOptions()
    options.add_argument(
        "--headless"
    )  # Note: because of the way this program downloads PDFs, driver MUST be run in headless mode. Otherwise we'll get errors.
    try:
        driver = webdriver.Chrome(
            executable_path=chrome_driver_path, options=options
        )  # Optional argument, if not specified will search path.
    except Exception as e:
        logging.error("Something went wrong when attempting to initialize "
                      "chromedriver")
        logging.exception(e)
        raise

    # add missing support for chrome "send_command"  to selenium webdriver. This only works in headless mode.
    driver.command_executor._commands["send_command"] = (
        "POST",
        "/session/$sessionId/chromium/send_command",
    )
    params = {
        "cmd": "Page.setDownloadBehavior",
        "params": {"behavior": "allow", "downloadPath": download_path},
    }
    command_result = driver.execute("send_command", params)
    logging.info("response from browser:")
    for key in command_result:
        logging.info("result:" + key + ":" + str(command_result[key]))

    #####################
    # Sets how long driver waits when things go wrong
    driver.implicitly_wait(5)

    logging.info("Chrome initialized")
    return driver
