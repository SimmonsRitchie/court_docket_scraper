# Pa court docket scraper

This program scrapes PDFs from Pennsylvania's Unified Judicial System [web portal](https://ujsportal.pacourts.us/DocketSheets/MDJ.aspx) and emails a list to a chosen email address.

## Motivation

Hundreds of district court dockets are uploaded to the UJS portal each day. The district courts are the first step in Pa.'s judicial system and so our reporters check these dockets each day in search of new arrests that might be newsworthy.

Unfortunately, the UJS website is slow and cumbersome. To check why a person was arrested, reporters must typically sift through scores of individual PDFs. Checking dockets for several counties can take upwards of an hour.

This program takes the work out of that task. It parses all of the PDFs for selected counties, extracts the info we want (eg. charges, bail amount, DOB of individual), and then emails a list of that info to a selected email address (or addresses). The list includes links to the relevant PDFs.

If any person has been charged with homicide, that will be noted in the email's subject line.

You can easily modify the program to scrape dockets for any Pennsylvania county you would like. If you have access to an EC2 instance, you can also use crontabs to run this program each day or several times per day automatically.

## Getting started

### Prerequisites

To run this program, you'll need python 3.6+. You'll also need a copy of 'chromedriver', which is included in this repo. Chromedriver is an executable used to control Chrome. It's maintained by the Chromium team.

You'll also need to have a number of python libraries installed. This program makes heavy use of selenium for scraping, pdfminer for parsing the pdfs, and pandas for cleaning and sorting the scraped data.

Before running, you'll want to open up your terminal and pip install the following:

selenium
pandas
pdfminer
email.mime.text
smtplib

### Configuration

In order for the program to send you an email with summarized docket info, you'll need a gmail account. The program will log into this account to do the actual sending. You'll likely need to make sure that your gmail settings allow "less secure app access". You can find this under security settings.

If you don't feel comfortable adjusting this setting on your personal gmail address, I suggest creating a new one. 

When you have decided on what gmail address to use. Create a file called config.py at the root of the program directory and add a dictionary called 'config':

Copy and paste the text below and where indicated in caps, replace with your own values. You can enter as many destination email addresses or counties you would like to scrape as you'd like. County names are not case sensitive.:

If you clone this repo, chromedriver should be included. Make sure you include the full path of it in the area indicated below, not it's relative path.

    config = {
        "email": {
            'username': 'ENTER_YOUR_GMAIL_ADDRESS',
            'pass': 'ENTER_YOUR_PASSWORD'
        },
        "destination": [
            "ENTER_EMAIL_DESTINATION"
        ],
        "county_list": ["COUNTY","COUNTY","COUNTY"],
        "chrome_driver_path": "ENTER_FULL_PATH_OF_CHROME_DRIVER_ON_YOUR_LOCAL_MACHINE",
        'run_mode': 'local',
        'ec2': {
            "base_folder_pdfs": "",
            "base_folder_email": "",
            "base_folder_text": "",
            "chrome_driver_path": ""
        }
    }

### Authors

Daniel Simmons-Ritchie, reporter at the Patriot-News/PennLive.com

### Note

This was the author's first major programming project so some (or a lot) of the code may be pretty wacky. It was a learning process.
