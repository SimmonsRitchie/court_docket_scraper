# Pa. court docket scraper

This program scrapes court data from Pennsylvania's Unified Judicial System [web portal](https://ujsportal.pacourts.us/DocketSheets/MDJ.aspx) and emails summarized info to selected email addresses.

### Prerequistes

- Python 3.6+

Note: ChromeDriver is included in this repo and should work on Mac without any additional setup. However, for Linux, you will likely need to install Chrome Driver yourself. Here's [a guide](https://tecadmin.net/setup-selenium-chromedriver-on-ubuntu/) to installing ChromeDriver on Ubuntu 16.04 and 18.04

### Install

1. Clone this repo.

2. If you don't have pipenv already installed, open the terminal and run:

    `pip install pipenv`

3.  From the terminal, cd into the project directory. Create a virtual environment using pipenv and install the project dependencies by running:

    `pipenv install
    `

3. You now need to configure the program to your specifications. Rename .env.example to .env:

    `mv .env.example .env`

4. Edit .env to your desired values:

    `nano .env`

    Note1: In order for the program to send emails with scrape output, you'll need a gmail account. The program will log into this account to do the actual sending. You'll likely need to make sure that your gmail settings allow "less secure app access". You can find this under gmail's security settings.
    
    If you don't feel comfortable adjusting this setting on your personal gmail address, I suggest creating a new one. 
    
    Note2: Make sure you include the full path of chromedriver on your system (included with this repo) and not it's relative path.

5. After you've saved and closed .env, you're ready to run the program. From the project directory, enter:

    `pipenv run python run.py`
    
    Depending on how many counties you've selected to scrape, it may take an hour or more for the program to finish.


## Motivation

Thousands of district court dockets are uploaded to Pennsylvania's UJS portal each day. For researchers and journalists, there is a treasure trove of information on this website.

Unfortunately, the UJS portal is slow and cumbersome to use. To check charges for a criminal case, a user must download a PDF of case information. Searching newly-filed cases in several counties can potentially take hours.

This program takes the work out of that task. It parses all of the PDFs for selected counties, extracts particular fields of interest (eg. charges, bail amount, DOB of individual), and then emails a list of that info to a selected email address (or addresses). The list includes links to the original PDF dockets for easy reference.

If any person has been charged with homicide, that will be noted in the email's subject line.

To make it easier to analyze scraped dockets or to use it in a web app, the program will also generate CSV and JSON files.

You can easily modify the program to scrape dockets for any Pennsylvania county you would like. If you have access to a Linux system, you can also use crontabs to run this program automatically each day or several times per day.

### Author

Daniel Simmons-Ritchie
