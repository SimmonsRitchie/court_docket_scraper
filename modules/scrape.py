"""
This module searches for court dockets on the UJC website, goes through each result, extracts docket info and the URL for each docket
"""

# Third party libs
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver.support.ui import Select
import sys
import time


def scrape_search_results(driver, url, county, scrape_date):

    ########################################################################
    #                     INPUT SEARCH
    ########################################################################

    """
    We begin our search by accessing the UJS website's search page, entering required fields, then hitting submit.
    """

    # Variables
    startdate = scrape_date
    enddate = startdate

    # Opening webpage
    print("Opening USC website")
    driver.get(url)

    try:
        # selecting search type
        print("Selecting search type")
        input_searchtype = Select(
            driver.find_element_by_xpath(
                '//*[@id="ctl00_ctl00_ctl00_cphMain_cphDynamicContent_ddlSearchType"]'
            )
        )
        input_searchtype.select_by_visible_text("Date Filed")

        # selecting start date
        print("Entering start date: {}".format(startdate))
        xpath_startdate = '//*[@id="ctl00_ctl00_ctl00_cphMain_cphDynamicContent_cphSearchControls_udsDateFiled_drpFiled_beginDateChildControl_DateTextBox"]'
        input_startdate = driver.find_element_by_xpath(xpath_startdate)

        input_startdate.clear()
        input_startdate.send_keys(str(startdate))

        # selecting end date
        print("Entering end date: {}".format(enddate))
        input_enddate = driver.find_element_by_xpath(
            '//*[@id="ctl00_ctl00_ctl00_cphMain_cphDynamicContent_cphSearchControls_udsDateFiled_drpFiled_endDateChildControl_DateTextBox"]'
        )
        input_enddate.clear()
        input_enddate.send_keys(str(enddate))

        # selecting county
        print("")
        print("###########")
        print("Beginning search of dockets in {} County".format(county.upper()))
        print("")
        input_county = Select(
            driver.find_element_by_xpath(
                '//*[@id="ctl00_ctl00_ctl00_cphMain_cphDynamicContent_cphSearchControls_udsDateFiled_ddlCounty"]'
            )
        )
        input_county.select_by_visible_text(county)

        # Starting loop that searches through all courts in county
        print("Scraping search results...")
    except NoSuchElementException:
        print("ERROR: Something went wrong while looking for input fields")
        print("USJ page might be down for maintenance")
        print("Close Chrome")
        print("Closing program")
        driver.quit()
        sys.exit(1)

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
    court = 1 # district court counter
    while search_courts_loop:
        try:
            # select district court
            print("Selecting court: {}".format(court))
            time.sleep(3) # we use sleep to give UJS website time to load
            input_court = Select(
                driver.find_element_by_xpath(
                    '//*[@id="ctl00_ctl00_ctl00_cphMain_cphDynamicContent_cphSearchControls_udsDateFiled_ddlCourtOffice"]'
                )
            )
            input_court.select_by_index(court)

            # submit form
            print("Submitting form")
            driver.find_element_by_xpath(
                '//*[@id="ctl00_ctl00_ctl00_cphMain_cphDynamicContent_btnSearch"]'
            ).click()
            court += 1

            # LOOP 2: RESULTS PAGES FOR EACH COURT
            print("Beginning page search loop")
            search_pages_loop = True
            page_count = 1 # page result counter
            while search_pages_loop:
                time.sleep(4)

                # LOOP 3: ROWS FOR EACH RESULTS PAGE
                search_rows_loop = True
                row_count = 1 # row counter
                print("Searching page {}...".format(page_count))
                while search_rows_loop:
                    print("Searching row {}...".format(row_count))
                    row_count += 1
                    xpath_substring = str("%02d" % (row_count,)) # Xpaths in some columns use leading zeros so use this substring to amend those xpaths.

                    # Checking whether row exists
                    try:
                        docketnum = driver.find_element_by_xpath(
                            "/html/body/form/div[3]/div[2]/table/tbody/tr/td/div[2]/div/div[3]/div/table/tbody/tr[1]/td/div/div[2]/table/tbody/tr["
                            + str(row_count)
                            + "]/td[2]"
                        )
                        clean_docketnum = docketnum.text

                        # If docketnum is a criminal docket then capture information
                        if "-CR-" in clean_docketnum:
                            print("Criminal case FOUND - saving")
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
                                "docket_num": clean_docketnum,
                                "caption": clean_caption,
                                "dob": clean_dob,
                                "filing_date": clean_filing_date,
                                "url": clean_docket_url,
                            }

                            # Display docket info
                            for key, value in docket.items():
                                print(f"{key.upper()}: {value}")

                            docket_list.append(docket) # Add docket to payload

                        # if not a criminal docket then move on to next row.
                        else:
                            print("Not a criminal case")

                    # No row found: End row search loop
                    except NoSuchElementException:
                        print("No row found")
                        break # End row search loop
                    except StaleElementReferenceException:
                        print("ERROR: Tried to find element but it has become stale")

                # Checking whether there are more pages
                try:
                    print("Checking if there are more pages...")
                    next_page = str(page_count + 1)
                    driver.find_element_by_link_text(next_page).click()
                    print("More pages FOUND - going to next page")
                    page_count += 1

                # No pages found: End page search loop
                except NoSuchElementException:
                    print("No further pages found")
                    break

        # No further court found: End court search loop
        except NoSuchElementException:
            print("No more courts found")
            break
    return docket_list
