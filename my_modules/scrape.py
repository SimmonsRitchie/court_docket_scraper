"""
This module searches for court dockets on the UJC website, goes through each result, extracts docket info and the URL for each docket
"""

#Load selenium modules

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support.ui import Select

# Other modules
import sys
import time
from collections import namedtuple


# My modules
from my_modules import misc

# Named tuple
DocketData = namedtuple("DocketData", ('case', 'docket_num', 'filing_date', 'dob','docket_url'))


def scrape_search_results(driver, url, county):
    #Variables
    startdate = misc.yesterday_date()
    enddate = startdate


    # Opening webpage
    print("Opening USC website")
    driver.get(url)

    try:
        #selecting search type
        print("Selecting search type")
        input_searchtype = Select(driver.find_element_by_xpath(
            '//*[@id="ctl00_ctl00_ctl00_cphMain_cphDynamicContent_ddlSearchType"]'
        ))
        input_searchtype.select_by_visible_text('Date Filed')

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
        input_county = Select(driver.find_element_by_xpath(
            '//*[@id="ctl00_ctl00_ctl00_cphMain_cphDynamicContent_cphSearchControls_udsDateFiled_ddlCounty"]'
        ))
        input_county.select_by_visible_text(county)

        # Starting loop that searches through all courts in county
        print("Scraping search results...")
        # Creating lists to store docket info from search results
        docketnum_list = []
        case_list = []
        filing_date_list = []
        dob_list = []
        docket_url_list = []
    except NoSuchElementException:
        print("ERROR: Something went wrong while looking for input fields")
        print("USJ page might be down for maintenance")
        print('Close Chrome')
        print("Closing program")
        driver.quit()
        sys.exit(1)


    search_courts_loop = True
    court = 1
    while search_courts_loop is True:
        try:
            # selecting court
            print("Selecting court: {}".format(court))
            time.sleep(3)
            input_court = Select(driver.find_element_by_xpath(
                '//*[@id="ctl00_ctl00_ctl00_cphMain_cphDynamicContent_cphSearchControls_udsDateFiled_ddlCourtOffice"]'
            ))
            # input_court.select_by_value(str(court))
            input_court.select_by_index(court)

            # Submit form
            print("Submitting form")
            driver.find_element_by_xpath(
                '//*[@id="ctl00_ctl00_ctl00_cphMain_cphDynamicContent_btnSearch"]'
            ).click()

            # Adding 1 to court index
            court += 1
            print("Beginning page search loop")
            search_pages_loop = True
            page_count = 1
            while search_pages_loop is True:
                time.sleep(4)
                search_rows_loop = True
                row_count = 1
                print("Searching page {}...".format(page_count))
                while search_rows_loop is True:
                    print("Searching row {}...".format(row_count))
                    row_count += 1
                    #Xpaths in some columns use leading zeros. Variable below is used to capture these.
                    xpath_subelement = str("%02d" % (row_count,))
                    try:
                        docketnum = driver.find_element_by_xpath(
                            '/html/body/form/div[3]/div[2]/table/tbody/tr/td/div[2]/div/div[3]/div/table/tbody/tr[1]/td/div/div[2]/table/tbody/tr[' + str(row_count) + ']/td[2]'
                        )
                        clean_docketnum = docketnum.text
                        # If docketnum is a criminal docket then capture information
                        if "-CR-" in clean_docketnum:
                            print("Criminal case FOUND - saving")
                            caption = driver.find_element_by_xpath(
                                '//*[@id="ctl00_ctl00_ctl00_cphMain_cphDynamicContent_cphResults_gvDocket_ctl' + xpath_subelement + '_Label2"]'
                            )
                            clean_caption = caption.text

                            filing_date = driver.find_element_by_xpath(
                                '/html/body/form/div[3]/div[2]/table/tbody/tr/td/div[2]/div/div[3]/div/table/tbody/tr[1]/td/div/div[2]/table/tbody/tr[' + str(row_count) + ']/td[5]'
                            )
                            clean_filing_date = filing_date.text

                            dob = driver.find_element_by_xpath(
                                '/html/body/form/div[3]/div[2]/table/tbody/tr/td/div[2]/div/div[3]/div/table/tbody/tr[1]/td/div/div[2]/table/tbody/tr[' + str(row_count) + ']/td[12]/table/tbody/tr/td/span'
                            )
                            clean_dob = dob.text

                            docket_url = driver.find_element_by_xpath(
                                '//*[@id="ctl00_ctl00_ctl00_cphMain_cphDynamicContent_cphResults_gvDocket_ctl' + str(xpath_subelement) + '_ucPrintControl_printMenun1"]/td/table/tbody/tr/td/a'
                            )
                            clean_docket_url = docket_url.get_attribute("href")

                            print("Docket num: {}".format(clean_docketnum))
                            print("Caption: {}".format(clean_caption))
                            print("DOB: {}".format(clean_dob))
                            print("Filing date: {}".format(clean_filing_date))
                            print("URL: {}".format(clean_docket_url))

                            docketnum_list.append(clean_docketnum)
                            case_list.append(clean_caption)
                            filing_date_list.append(clean_filing_date)
                            dob_list.append(clean_dob)
                            docket_url_list.append(clean_docket_url)
                        else:
                            print("Not a criminal case")
                    except NoSuchElementException:
                        print("No row found")
                        break
                    except StaleElementReferenceException:
                        print("ERROR: Tried to find element but it's become stale")
                try:
                    #Attempting to click next page if it exists
                    print("Checking if there are more pages...")
                    next_page = str(page_count + 1)
                    driver.find_element_by_link_text(next_page).click()
                    print("More pages FOUND - going to next page")
                    #Adding to page counter
                    page_count += 1
                except NoSuchElementException:
                    print("No further pages found")
                    break
        except NoSuchElementException:
            print("No more courts found")
            break
    return DocketData(case_list,docketnum_list,filing_date_list,dob_list,docket_url_list)


