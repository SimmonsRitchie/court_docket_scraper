# PENNSYLVANIA COURT DOCKET SCRAPER

This program scrapes PDFs from Pennsylvania's Unified Judicial System [web portal](https://ujsportal.pacourts.us/DocketSheets/MDJ.aspx) and emails a list to a chosen email address.

Hundreds of district court dockets are uploaded to this portal each day. The district courts are the first step in Pa.'s judicial system and so our reporters check these dockets each day in search of new arrests that might be newsworthy.

Unfortunately, the UJS website is slow and cumbersome. To check why a person was arrested, reporters must typically sift through scores of individual PDFs. Checking dockets for several counties can take upwards of an hour.

This program takes the work out of that task. It parses all of the PDFs for selected counties, extracts the info we want (eg. charges, bail amount, DOB of individual), and then emails a list of that info to a selected email address (or addresses). The list includes links to the relevant PDFs.

If any person has been charged with homicide, that will be noted in the email's subject line.

You can easily modify the program to scrape specific Pennsylvania counties. If you have access to an EC2 server, you can also use crontabs to run this program each day.

## Getting started

### Prerequisites

To run, you'll need python 3.6. You'll also need a copy of 'chromedriver', which is included in this repo.

### Configuration

In order for the program to send you an email with summarized docket info, you'll need a gmail account. This account does the actual sending. You'll likely need to make sure that your gmail settings allow "Less secure app access". You can find this under security settings.

If you don't feel comfortable adjusting this setting on your personal gmail address, I suggest creating a new one. 

When you have decided on what gmail address to use. Create a file called config.py at the root of the program directory and add a dictionary called 'config':

Where indicated in caps, replace with your own values:

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
