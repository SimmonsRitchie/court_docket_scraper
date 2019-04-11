# Pa. court docket scraper

This program scrapes PDFs from Pennsylvania's Unified Judicial System [web portal](https://ujsportal.pacourts.us/DocketSheets/MDJ.aspx) and emails summarized info about those dockets to selected email addresses.

## Motivation

Hundreds of district court dockets are uploaded to the UJS portal each day. The district courts are the first step in Pa.'s judicial system and so our reporters check these dockets each day in search of new arrests that might be newsworthy.

Unfortunately, the UJS website is slow and cumbersome. To check why a person was arrested, reporters must typically sift through scores of individual PDFs. Checking dockets for several counties can take upwards of an hour.

This program takes the work out of that task. It parses all of the PDFs for selected counties, extracts the info we want (eg. charges, bail amount, DOB of individual), and then emails a list of that info to a selected email address (or addresses). The list includes links to the original PDF dockets for easy reference.

If any person has been charged with homicide, that will be noted in the email's subject line.

To make it easier to analyze scraped dockets or to use it in a web app, the program will also generate CSV and JSON files.

You can easily modify the program to scrape dockets for any Pennsylvania county you would like. If you have access to an EC2 instance, you can also use crontabs to run this program each day or several times per day automatically.

## Getting started

### Prerequisites

To run this program, you'll need python 3.6+. You'll also need a copy of 'chromedriver', which is included in this repo. Chromedriver is an executable used to control Chrome. It's maintained by the Chromium team.

You'll also need to have a number of python libraries installed. This program makes heavy use of selenium, which uses chromedriver to conduct the scrape, pdfminer for parsing the pdfs, and pandas for cleaning and sorting the scraped data.

Before running, you'll want to open up your terminal and pip install the following:

selenium
pandas
pdfminer
email.mime.text
smtplib

Make sure your version of Pandas is 0.23 or higher otherwise you may encounter errors.

### Configuration

In order for the program to send emails with summarized docket info, you'll need a gmail account. The program will log into this account to do the actual sending. You'll likely need to make sure that your gmail settings allow "less secure app access". You can find this under security settings.

If you don't feel comfortable adjusting this setting on your personal gmail address, I suggest creating a new one. 

When you have decided on what gmail address to use. Create a file called config.py at the root of the program directory and add a dictionary called 'config':

Copy and paste the text below and where indicated in caps, replace with your own values. You can enter as many destination email addresses or counties you would like to scrape as you'd like. County names are not case sensitive.

Make sure you include the full path of chromedriver on your system (included with this repo) and not it's relative path.

    config = {
        "email": {
            'username': 'ENTER_YOUR_GMAIL_ADDRESS',
            'pass': 'ENTER_YOUR_PASSWORD'
        },
        "destination": [
            "ENTER_EMAIL_DESTINATION_1",
            "ENTER_EMAIL_DESTINATION_2",
            "ENTER_EMAIL_DESTINATION 3"
        ],
        "county_list": ["COUNTY1","COUNTY2","COUNTY3"],
        "desired_scrape_date": "yesterday", # enter "today" to scrape today's dockets
        "chrome_driver_path": "ENTER_FULL_PATH_OF_CHROME_DRIVER_ON_YOUR_LOCAL_MACHINE",
        'run_mode': 'local',
        'ec2': {
            "base_folder_pdfs": "",
            "base_folder_email": "",
            "base_folder_json": "",
            "base_folder_csv": "",
            "base_folder_text": "",
            "base_folder_email_template": "",
            "base_folder_final_email": "",
            "chrome_driver_path": ""
        }
    }

Note: Because the UJS website takes a while to upload new dockets, it's recommended that you set "desired_scrape_date" to "yesterday" if you want to capture most of that day's dockets. 

### Run

When you've set up the config file and installed the needed libraries, the program should be ready to run.

From the terminal, cd into the program's directory and then type 'python program.py'

### Authors

Daniel Simmons-Ritchie, reporter at the Patriot-News/PennLive.com

### Note

This was one of the author's first programming projects so some (or a lot) of the code may be pretty wacky. It was a learning process. If you have problems running this program, feel free to reach out.
