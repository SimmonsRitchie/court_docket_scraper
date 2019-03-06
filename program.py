
"""
UJC Scraper

Author: Daniel Simmons-Ritchie

"""

# My modules
from my_modules import delete, initialize, scrape, download, convert, email
from config import config


def main():
    url = "https://ujsportal.pacourts.us/DocketSheets/MDJ.aspx" #URL for UJC website

    # If running local/ec2 mode then change directories accordingly.
    # I did this because when the program runs on an EC2 server with crontabs it needs full paths.
    if config["run_mode"] == "local":
        base_folder_pdfs = "pdfs/"
        base_folder_email = "email_payload/"
        base_folder_text = "extracted_text/"
        chrome_driver_path = config["chrome_driver_path"]

    elif config["run_mode"] == "ec2":
        base_folder_pdfs = config["ec2"]["base_folder_pdfs"]
        base_folder_email = config["ec2"]["base_folder_email"]
        base_folder_text = config["ec2"]["base_folder_text"]
        chrome_driver_path = config["ec2"]["chrome_driver_path"]


    print("Starting scraper")

    # DELETE OLD FILES
    delete.delete_temp_files(base_folder_pdfs, base_folder_email, base_folder_text)

    # START CHROME DRIVER
    driver = initialize.initialize_driver(base_folder_pdfs, chrome_driver_path)


    # SCRAPE DOCKET DATA FOR EACH COUNTY
    for county in config["county_list"]:
        county = county.title() # ensures that county names are in title case, otherwise we'll get errors
        docketdata = scrape.scrape_search_results(driver, url, county)

        # IF THERE'S DATA THEN DOWNLOAD PDFS AND EXTRACT TEXT
        if docketdata:
            charges_list = []
            bail_list = []
            for x, y in enumerate(docketdata.docket_num):
                docket_num = docketdata.docket_num[x]
                docket_url = docketdata.docket_url[x]
                download.download_pdf(driver, docket_url, docket_num, base_folder_pdfs)
                text = convert.convert_pdf_to_text(docket_num, base_folder_pdfs, base_folder_text)

                # PARSE EXTRACTED PDF TEXT FOR CHARGES AND BAIL
                if text:
                    parseddata = convert.parse_extracted_text(text)
                    charges_list.append(parseddata.charge)
                    bail_list.append(parseddata.bail)
                else:
                    print("Error: no extracted text found")
                    charges_list.append("Error: Check docket")
                    bail_list.append("Error: check docket")
                print("Clean version of extracted charge and bail:")
                print(docket_num)
                print(parseddata.charge)
                print(parseddata.bail)

            # CREATE DICTIONARY OF ALL DOCKET DATA FOR EMAIL
            create_dict = {
                "Name": docketdata.case,
                "Filing date": docketdata.filing_date,
                "DOB": docketdata.dob,
                "Charges": charges_list,
                "Bail": bail_list,
                "URL": docketdata.docket_url
            }
            email.email_payload(base_folder_email, create_dict, county)

    # SEND EMAIL WITH DOCKET DATA
    email.email_notification(base_folder_email, config["destination"], config["email"])

    # CLOSE PROGRAM
    print("Closing program")



# Start main loop if running from program.py
if __name__ == '__main__':
    main()