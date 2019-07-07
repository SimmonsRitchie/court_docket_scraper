# Pa. court docket scraper

This program scrapes PDFs from Pennsylvania's Unified Judicial System [web portal](https://ujsportal.pacourts.us/DocketSheets/MDJ.aspx) and emails summarized info about those dockets to selected email addresses.

### Install

1. Clone this repo.

2. In the terminal, cd into the project directory. Create a virtual environment using pipenv and load the project dependencies:

    `pipenv install
    `

3. Copy and rename .env.example as .env:

    `cp .env.example .env`

4. The .env file contains configuraton files for the program. Edit it to your desired values.

    `nano .env`

    In order for the program to send emails with scrape output, you'll need a gmail account. The program will log into this account to do the actual sending. You'll likely need to make sure that your gmail settings allow "less secure app access". You can find this under security settings.
    
    If you don't feel comfortable adjusting this setting on your personal gmail address, create a new one. 
    
    Also: Make sure you include the full path of chromedriver on your system (included with this repo) and not it's relative path.

5. After you've saved and closed .env, you're ready to run the program. From the project directory, enter:

    `pipenv run python run.py`


## Motivation

Hundreds of district court dockets are uploaded to the UJS portal each day. The district courts are the first step in Pa.'s judicial system and so our reporters check these dockets each day in search of new arrests that might be newsworthy.

Unfortunately, the UJS website is slow and cumbersome. To check why a person was arrested, reporters must typically sift through scores of individual PDFs. Checking dockets for several counties can take upwards of an hour.

This program takes the work out of that task. It parses all of the PDFs for selected counties, extracts the info we want (eg. charges, bail amount, DOB of individual), and then emails a list of that info to a selected email address (or addresses). The list includes links to the original PDF dockets for easy reference.

If any person has been charged with homicide, that will be noted in the email's subject line.

To make it easier to analyze scraped dockets or to use it in a web app, the program will also generate CSV and JSON files.

You can easily modify the program to scrape dockets for any Pennsylvania county you would like. If you have access to a Linux system, you can also use crontabs to run this program automatically each day or several times per day.

### Authors

Daniel Simmons-Ritchie, reporter at the Patriot-News/PennLive.com
