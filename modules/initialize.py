"""
This module initializes Chrome Driver in headless mode.

It also includes a hacky workaround to ensure that Chrome driver will download PDFs in headless mode. This is due to a
bug in Selenium/ChromeDriver. Note: I don't use Requests library to download PDFs because changes to USJ website meant
that it no longer worked.
"""

# Load selenium modules
from selenium import webdriver
import os

# project modules
from locations import test_dirs

def initialize_driver():

    print("\nInitializing Chrome")

    # SET CONFIG VARS
    chrome_driver_path = os.environ.get("CHROME_DRIVER_PATH")
    download_path = str(test_dirs["pdfs"]) # must be string, not Path instance

    print("Driver download directory:", download_path)
    print("All files will be downloaded to this path")

    # Chrome options + initialize
    options = webdriver.ChromeOptions()
    options.add_argument(
        "--headless"
    )  # Note: because of the way this program downloads PDFs, driver MUST be run in headless mode. Otherwise we'll get errors.
    driver = webdriver.Chrome(
        executable_path=chrome_driver_path, options=options
    )  # Optional argument, if not specified will search path.

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
    print("response from browser:")
    for key in command_result:
        print("result:" + key + ":" + str(command_result[key]))

    #####################
    # Sets how long driver waits when things go wrong
    driver.implicitly_wait(5)

    return driver
