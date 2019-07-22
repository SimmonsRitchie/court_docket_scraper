# Pa. court docket scraper

This program scrapes court data from Pennsylvania's Unified Judicial System [web portal](https://ujsportal.pacourts.us/DocketSheets/MDJ.aspx) and emails summarized info to selected email addresses.

### Prerequistes

- Python 3.6+

- ChromeDriver is included in this repo and should work on Mac without any 
additional setup. However, for Linux, you will likely need to install Chrome Driver yourself. Here's [a guide](https://tecadmin.net/setup-selenium-chromedriver-on-ubuntu/) to installing ChromeDriver on Ubuntu 16.04 and 18.04

- In order for the program to send emails with scrape output, you'll need a 
gmail account. The program will log into this account to do the actual sending. You'll likely need to make sure that your gmail settings allow "less secure app access". You can find this under gmail's security settings. If you don't feel comfortable adjusting this setting on your personal gmail address, I suggest creating a new one. 

### Install

1. Clone this repo by either clicking Github's 'clone or download' button or,
 in the terminal, navigating to where you would like the 
scraper to exist on your system and running:

    `git clone https://github.com/SimmonsRitchie/court_docket_scraper.git`

2. If you don't have pipenv already installed, run:

    `pip install pipenv`

3. Navigate into the project directory:

    `cd court_docket_scraper`
     
4. Use pipenv to create a virtual environment and install the project 
dependencies. Run:

    `pipenv install`

5. You now need to configure the program. Rename .env.example to .env:

    `mv .env.example .env`

6. Edit .env to your desired values (eg. counties you would like to scrape, 
etc):

    `nano .env`

    Note: for CHROME_DRIVER_PATH, make sure you include the full path of 
    chromedriver on your system (included with this repo) and not it's relative path.

7. After you've saved and closed .env, you're ready to run the program. From
 the project directory, enter:

    `pipenv run python run.py`
    
    Depending on how many counties you've selected to scrape, it may take an hour or more for the program to finish.
    
8. OPTIONAL: If you use Linux, I recommend setting a cron job so that the 
scraper runs at a specific time each day, each week, etc. Here's [a guide](https://www.liquidweb.com/kb/create-a-cron-task-in-ubuntu-16-04/) on 
how to set up a cron job for Ubuntu 16.04.

    You can also configure pipenv to run the scraper using specific 
configuration settings. Eg. you might like to have one cron job that scrapes
 certain counties in the morning and another cron job that runs the scraper 
 later in the day to scrape different counties.
 
    To do this, first make a copy of the existing .env file and give it a 
    different name (e.g. '
 .morning.env', '.afternoon.env'). Adjust the settings as you like. You can 
 then create a shell script that 
 tells pipenv to run that specific .env file. You can do this by first 
 running: `nano 
 morning.sh` and then 
 saving something like:
 

```
# Morning scraper script

# This tells pipenv to use this .env file
export PIPENV_DOTENV_LOCATION="/home/MyName/court_docket_scraper/.morning.env"
# Navigate to scraper project directory
cd /home/MyName/court_docket_scraper/
# Run scraper
pipenv run python run.py`
```

Then, in your cron tab, you can enter something like this to run the script 
each day at 8:01am:

```1 8 * * * sh /home/MyName/court_docket_sraper/morning.sh```
 

## Motivation

Thousands of district court dockets are uploaded to Pennsylvania's UJS portal each day. For researchers and journalists, there is a treasure trove of information on this website.

Unfortunately, the UJS portal is slow and cumbersome to use. To check charges for a criminal case, a user must download a PDF of case information. Searching newly-filed cases in several counties can potentially take hours.

This program takes the work out of that task. It parses all of the PDFs for selected counties, extracts particular fields of interest (eg. charges, bail amount, DOB of individual), and then emails a list of that info to a selected email address (or addresses). The list includes links to the original PDF dockets for easy reference.

If any person has been charged with homicide, that will be noted in the email's subject line.

To make it easier to analyze scraped dockets or to use it in a web app, the program will also generate CSV and JSON files.

You can easily modify the program to scrape dockets for any Pennsylvania county you would like. If you have access to a Linux system, you can also use crontabs to run this program automatically each day or several times per day.

### Author

Daniel Simmons-Ritchie
