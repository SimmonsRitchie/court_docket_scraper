"""
This module searches for court dockets on the UJC website, goes through each result, extracts docket info and the URL for each docket
"""

# inbuilt or third party libs
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver.support.ui import Select
import sys
import time
import logging
from typing import List

# project modules
from modules.misc import clean_list_of_dicts


def scrape_search_results(driver: object, county: str, scrape_date: str) -> List:

    """
    Scrape the search results of the UJS website. Returns a list of dicts with case information.

    """
    logging.info("Beginning scrape of Pa. Unified Judicial System portal")

    ########################################################################
    #                     INPUT: SEARCH TERMS
    ########################################################################

    """
    We begin our search by accessing the UJS website's search page, entering required fields, then hitting submit.
    """

    # Variables
    startdate = scrape_date
    enddate = startdate
    url = "https://ujsportal.pacourts.us/DocketSheets/MDJ.aspx"  # URL for UJC website

    # Opening webpage
    logging.info(f"Opening: {url}")
    driver.get(url)

    try:
        # selecting search type
        logging.info("Selecting search type")
        input_searchtype = Select(
            driver.find_element_by_xpath(
                '//*[@id="ctl00_ctl00_ctl00_cphMain_cphDynamicContent_ddlSearchType"]'
            )
        )
        input_searchtype.select_by_visible_text("Date Filed")

        # selecting start date
        logging.info("Entering start date: {}".format(startdate))
        xpath_startdate = '//*[@id="ctl00_ctl00_ctl00_cphMain_cphDynamicContent_cphSearchControls_udsDateFiled_drpFiled_beginDateChildControl_DateTextBox"]'
        input_startdate = driver.find_element_by_xpath(xpath_startdate)

        input_startdate.clear()
        input_startdate.send_keys(str(startdate))

        # selecting end date
        logging.info("Entering end date: {}".format(enddate))
        input_enddate = driver.find_element_by_xpath(
            '//*[@id="ctl00_ctl00_ctl00_cphMain_cphDynamicContent_cphSearchControls_udsDateFiled_drpFiled_endDateChildControl_DateTextBox"]'
        )
        input_enddate.clear()
        input_enddate.send_keys(str(enddate))

        # selecting county
        logging.info("Beginning search of dockets in {} County".format(county.upper()))
        input_county = Select(
            driver.find_element_by_xpath(
                '//*[@id="ctl00_ctl00_ctl00_cphMain_cphDynamicContent_cphSearchControls_udsDateFiled_ddlCounty"]'
            )
        )
        input_county.select_by_visible_text(county)

        # Starting loop that searches through all courts in county
        logging.info("Scraping search results...")
    except NoSuchElementException as e:
        # If no input fields are found that's a serious error that suggests the UJS website might be down or has
        # undergone a major change
        logging.error("Something went wrong while looking for input fields")
        logging.exception(e)
        driver.quit()
        raise

    ########################################################################
    #                     SCRAPE SEARCH RESULTS
    ########################################################################

    """
    We now use a series of nested loops to scrape the search results:
    
    -> Loop1: Cycle through all district courts
    --> Loop2: Cycle through all result pages for each district court
    ---> Loop3: Cycle through all rows on each results page
    
    Loops break when no further courts/pages/rows are found.
    """

    # Payload
    docket_list = []

    # LOOP 1: DISTRICT COURTS
    search_courts_loop = True
    court = 1  # district court counter
    while search_courts_loop:
        try:
            # select district court
            logging.info("Selecting court: {}".format(court))
            time.sleep(3)  # we use sleep to give UJS website time to load
            input_court = Select(
                driver.find_element_by_xpath(
                    '//*[@id="ctl00_ctl00_ctl00_cphMain_cphDynamicContent_cphSearchControls_udsDateFiled_ddlCourtOffice"]'
                )
            )
            input_court.select_by_index(court)

            # submit form
            logging.info("Submitting form")
            driver.find_element_by_xpath(
                '//*[@id="ctl00_ctl00_ctl00_cphMain_cphDynamicContent_btnSearch"]'
            ).click()
            court += 1

            # LOOP 2: RESULTS PAGES FOR EACH COURT
            search_pages_loop = True
            page_count = 1  # page result counter
            logging.info("Beginning page search loop")
            while search_pages_loop:
                time.sleep(4)

                # LOOP 3: ROWS FOR EACH RESULTS PAGE
                search_rows_loop = True
                row_count = 1  # row counter
                logging.info("Searching page {}...".format(page_count))
                logging.info("Starting row search loop...")
                while search_rows_loop:
                    logging.info(
                        f"Checking whether row {row_count} exists...".format(row_count)
                    )
                    row_count += 1 # Be wary of moving this counter, it plays an important part in finding
                    # row elements in this loop
                    xpath_substring = str(
                        "%02d" % (row_count,)
                    )  # Xpaths in some columns use leading zeros so use this substring to amend those xpaths.

                    # Checking whether row exists
                    try:
                        docketnum = driver.find_element_by_xpath(
                            "/html/body/form/div[3]/div[2]/table/tbody/tr/td/div[2]/div/div[3]/div/table/tbody/tr[1]/td/div/div[2]/table/tbody/tr["
                            + str(row_count)
                            + "]/td[2]"
                        )
                        clean_docketnum = docketnum.text
                        logging.info(f"Row {row_count} exists")
                        logging.info(
                            f"Checking whether row {row_count} contains a criminal case..."
                        )

                        # If docketnum is a criminal docket then capture information
                        if "-CR-" in clean_docketnum:
                            logging.info("Criminal case FOUND - saving")
                            caption = driver.find_element_by_xpath(
                                '//*[@id="ctl00_ctl00_ctl00_cphMain_cphDynamicContent_cphResults_gvDocket_ctl'
                                + xpath_substring
                                + '_Label2"]'
                            )
                            clean_caption = caption.text

                            filing_date = driver.find_element_by_xpath(
                                "/html/body/form/div[3]/div[2]/table/tbody/tr/td/div[2]/div/div[3]/div/table/tbody/tr[1]/td/div/div[2]/table/tbody/tr["
                                + str(row_count)
                                + "]/td[5]"
                            )
                            clean_filing_date = filing_date.text

                            dob = driver.find_element_by_xpath(
                                "/html/body/form/div[3]/div[2]/table/tbody/tr/td/div[2]/div/div[3]/div/table/tbody/tr[1]/td/div/div[2]/table/tbody/tr["
                                + str(row_count)
                                + "]/td[12]/table/tbody/tr/td/span"
                            )
                            clean_dob = dob.text

                            docket_url = driver.find_element_by_xpath(
                                '//*[@id="ctl00_ctl00_ctl00_cphMain_cphDynamicContent_cphResults_gvDocket_ctl'
                                + str(xpath_substring)
                                + '_ucPrintControl_printMenun1"]/td/table/tbody/tr/td/a'
                            )
                            clean_docket_url = docket_url.get_attribute("href")

                            docket = {
                                "county": county,
                                "docketnum": clean_docketnum,
                                "case_caption": clean_caption,
                                "dob": clean_dob,
                                "filing_date": clean_filing_date,
                                "url": clean_docket_url,
                            }

                            # Display docket info
                            for key, value in docket.items():
                                logging.info(f"{key.upper()}: {value}")

                            docket_list.append(docket)  # Add docket to payload

                        # if not a criminal docket then move on to next row.
                        else:
                            logging.info("Not a criminal case, moving on.")

                    # BREAK LOOP 3: No more rows found
                    except NoSuchElementException:
                        logging.info(f"Row {row_count} doesn't exist")
                        logging.info("Ending row search loop")
                        break  # End row search loop
                    except StaleElementReferenceException as e:
                        # this suggests the UJS website might be down or search results aren't loading properly
                        logging.error("Element has become stale")
                        logging.exception(e)
                        raise

                # Checking whether there are more pages
                try:
                    logging.info("Checking if there are more pages...")
                    next_page = str(page_count + 1)
                    driver.find_element_by_link_text(next_page).click()
                    logging.info("More pages FOUND - going to next page")
                    page_count += 1

                # BREAK LOOP 2: No more pages found
                except NoSuchElementException:
                    logging.info("No further pages found")
                    logging.info("Ending page search loop")
                    break

        # BREAK LOOP 1: No further district courts found
        except NoSuchElementException:
            logging.info("No more courts found")
            logging.info("Ending court search loop")
            break

    # CLEAN DATA
    # All cases should have unique docketnums but we remove any duplicates just in case because they can cause errors.
    if docket_list:  # we only clean if we have data
        docket_list = clean_list_of_dicts(docket_list)

    return docket_list
