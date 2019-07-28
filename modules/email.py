"""
This module handles sending auto email. It also converts dockets into an email friendly text file.
"""

# load email modules
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
import os
import json
import logging
from typing import List, Union, Optional
import pandas as pd
import time

# Load my modules
from modules import export
from modules.misc import get_datetime_now_formatted, detect_keyword_in_df
from locations import dirs, paths


def email_error_notification(error_summary: str, full_error_msg: str) -> None:

    """ Assembles and sends an email notifying maintainer that there was an
    error during program run. """

    error_emails_enabled = False if os.environ.get("ERROR_EMAILS") == "FALSE" else True
    if not error_emails_enabled:
        logging.info(
            "Email error notifications are disabled\nNo error email will be sent"
        )
        return

    logging.info("Sending error notification to desiginated email addresses")

    # GET INFO FOR MESSAGE
    error_datetime = get_datetime_now_formatted()
    dir_email_template = dirs["email_template"]
    county_list = [
        x.title() for x in json.loads(os.environ.get("COUNTY_LIST"))
    ]  # Counties are transformed into print_title case
    target_scrape_day = os.environ.get("TARGET_SCRAPE_DATE", "yesterday").lower()

    pluralize_county = "county" if len(county_list) == 1 else "counties"
    mobile_tease_content = error_summary
    intro_content = (
        f"<p>{error_summary}</p>"
        f"<p>SETTINGS: Scraping {target_scrape_day}'s cases for {', '.join(county_list)} {pluralize_county}"
        f"<p>ERROR TIME: {error_datetime}.</p>"
    )
    body_content = (
        f"<div style='text-align:center;margin-left:20px;margin-right:20px'><p>ERROR:</p><p>"
        f"{full_error_msg}</p></div>"
    )
    footer_content = ""
    subject_line = "ERROR: something went wrong"

    # ATTACH ERROR LOG + CSV
    # Attach logs
    dir_latest_logs = dirs["logs_output"] / "latest"
    attachments = list(
        dir_latest_logs.glob("*info.log")
    )  # we get all files with this suffix

    # CREATE HTML PAYLOAD
    message = create_final_email_payload(
        dir_email_template,
        mobile_tease_content,
        intro_content,
        body_content,
        footer_content,
    )

    # SEND
    recipients = os.environ.get("DESTINATION_EMAIL_ADDRESS_FOR_ERRORS")
    if recipients:
        recipients = json.loads(recipients)
    else:
        # default recipients are the recipients who would normally receive
        # full scrape output
        recipients = json.loads(os.environ.get("DESTINATION_EMAIL_ADDRESSES"))

    login_to_gmail_and_send(recipients, message, subject_line, attachments)


def email_notification(
    scrape_start_datetime: object, scrape_end_datetime: object, target_scrape_day:
        str, county_list: List[
            str]
) -> None:

    """ Assembles and sends our email notification after successful scrape """

    logging.info("Sending email with scraped data...")

    # GET DATE INFO - NEEDED FOR CUSTOM MESSAGES
    scrape_end_date = scrape_end_datetime.strftime("%a, %b %-d %Y")
    yesterday_date = (datetime.now() - timedelta(1)).strftime("%a, %b %-d %Y")

    # GET NUM OF CASES
    if paths["payload_csv"].is_file():
        df = pd.read_csv(paths["payload_csv"])
        num_of_cases = len(df.index)
    else:
        num_of_cases = 0

    # GENERATE CUSTOM MESSAGES
    # Note: we add trailing white space in mobile test content so that actual
    # email content isn't included in tease.
    mobile_tease_content = gen_mobile_tease_content(county_list, num_of_cases)
    intro_content = gen_intro_content(
        county_list, num_of_cases, target_scrape_day, scrape_end_date,
        yesterday_date
    )
    footer_content = gen_footer_content(scrape_start_datetime,
                                        scrape_end_datetime, county_list)
    subject_line = create_subject_line(
        target_scrape_day, scrape_end_date, yesterday_date, county_list
    )

    # GET SCRAPED DATA
    scraped_data_content = paths["payload_email"].read_text()

    # CHECK FOR MURDER/HOMICIDE
    # Add a special message to subject line and mobile tease if either condition is met
    subject_line, mobile_tease_content = insert_special_message(
        mobile_tease_content, subject_line
    )
    # GENERATE EMAIL HTML
    # We take our HTML payload of docket data and wrap it in more HTML to make it look nice.
    message = create_final_email_payload(
        dirs["email_template"],
        mobile_tease_content,
        intro_content,
        scraped_data_content,
        footer_content,
    )

    # SAVE EMAIL HTML - FOR DEBUGGING PURPOSES
    export.save_copy_of_final_email(paths["email_final"], message)

    # ACCESS GMAIL AND SEND
    recipients = json.loads(os.environ.get("DESTINATION_EMAIL_ADDRESSES"))
    login_to_gmail_and_send(recipients, message, subject_line)


def gen_mobile_tease_content(county_list: List[str], num_of_cases) -> str:
    """This create a hidden message that appears as a preview in most email
    clients"""

    # GENERATE HIDDEN MESSAGE FOR MOBILE TEASE
    if len(county_list) == 1:
        mobile_tease_content = f"{num_of_cases} cases filed " \
                               f"in {county_list[0]} County."
    else:
        mobile_tease_content = (
            f"{num_of_cases} cases filed "
            f"in {', '.join(county_list)} counties."
        )
    return mobile_tease_content


def gen_intro_content(
    county_list: List[str],
    num_of_cases: int,
    target_scrape_day: str,
    formatted_time: str,
    yesterday_date: str,
) -> str:
    """This returns text that greets the email viewer when they open the
    email. It's positioned below the main header "Pa Court Report" but above
    the tables of scraped data"""

    # CUSTOMIZE TEXT FRAGMENT BASED ON NUM OF CASES
    if num_of_cases == 0:
        num_cases_text = "No criminal cases were"
    elif num_of_cases == 1:
        num_cases_text = "One criminal case was"
    else:
        num_cases_text = f"The following {num_of_cases} criminal cases " \
            f"were"

    # GENERATE INTRO
    # we create different intros based on conditions
    if len(county_list) == 1:
        if target_scrape_day == "today":
            intro_description = f"<p>{num_cases_text} filed " \
                f"in {county_list[0]} County today as of {formatted_time}.</p>"
        elif target_scrape_day == "yesterday":
            intro_description = f"<p>{num_cases_text} filed in {county_list[0]} County " \
                                 f"yesterday ({yesterday_date}).</p>"
    else:
        if target_scrape_day == "today":
            intro_description = f"<p>{num_cases_text} filed " \
                f"in district courts today as of {formatted_time}.</p>"\

        elif target_scrape_day == "yesterday":
            intro_description = f"<p>{num_cases_text} filed in district " \
                                f"courts yesterday ({yesterday_date}).</p>\
                        <p>You can also view a searchable list of these cases\
                        <a href='https://s3.amazonaws.com/court-dockets/index.html'>here</a>.</p>\
                    "
    scrape_name = os.getenv("SCRAPE_NAME", "Case Scrape")
    intro_subheading = f'<span class="subheading">{scrape_name}</span>'
    return intro_subheading + intro_description


def gen_footer_content(scrape_start_datetime: object, scrape_end_datetime:
    object, county_list: List) -> str:

    # GET DATE AND TIME FRAGMENTS
    scrape_start_date = scrape_start_datetime.strftime("%a, %b %-d %Y")
    scrape_start_time = scrape_start_datetime.strftime("%I:%M %p")
    scrape_end_date = scrape_end_datetime.strftime("%a, %b %-d %Y")
    scrape_end_time = scrape_end_datetime.strftime("%I:%M %p")
    scrape_duration = int(int(time.mktime(scrape_end_datetime.timetuple()) -
                              time.mktime(scrape_start_datetime.timetuple()))/ 60)
    duration_per_county = scrape_duration / len(county_list)

    if scrape_start_datetime.date() == scrape_end_datetime.date():
        date_text = f"{scrape_start_time} and {scrape_end_time} on {scrape_end_date}"
    else:
        date_text = f"{scrape_start_time}, {scrape_start_date} and " \
            f"{scrape_end_time}, {scrape_end_date}"

    # GENERATE FOOTER
    return f"<p>This information was scraped between {date_text} from the " \
        f"<a href='https://ujsportal.pacourts.us/DocketSheets/MDJ.aspx'>Pa. " \
        f"Unified Judicial Portal</a>. Scrape time: {scrape_duration} min " \
        f"({duration_per_county} min per county)</p>" \
        f"<p>Please note that new cases are not always immediately " \
        f"uploaded to the portal. The cases listed above may not represent " \
        f"all cases filed for the targeted date range.</p>\
        <p>This email was generated by a program written by " \
        f"Daniel Simmons-Ritchie. \
        If you don't wish to receive these emails or you see errors in this " \
        f"email, contact him at \
        <a href='mailto:dsimmons-ritchie@spotlight.org'>" \
        f"dsimmons-ritchie@spotlight.org</p>"


def insert_special_message(mobile_tease_content: str, subject_line: str
) -> tuple:
    """Detects whether specific keywords (eg. homicide, murder) is included
    in email content and then returns a tuple with an updated version of
    subject line and mobile tease"""

    # CHECKING ENV VAR PRESENT
    keyword_list = os.getenv("KEYWORD_ALERTS")
    if not keyword_list:
        logging.info("No KEYWORD_ALERTS have been specified in .env file, "
                     "no special message will be inserted")
        return subject_line, mobile_tease_content
    else:
        keyword_list = json.loads(keyword_list)
        logging.info(f"KEYWORD_ALERTS {keyword_list} are set in .env file")
    logging.info("Checking whether special message should be inserted in "
                 "email preview and subject line...")

    # CHECKING WHETHER CSV IS PRESENT
    if not paths["payload_csv"].is_file():
        logging.info("No payload CSV detected - no special message will be "
                     "inserted")
        return subject_line, mobile_tease_content

    # CHECK WHETHER KEYWORDS ARE IN DF
    df = pd.read_csv(paths["payload_csv"])
    keywords_found = []
    logging.info(
        f"Detecting whether the following keywords are in payload "
        "csv: {keyword_list}"
    )
    for keyword in keyword_list:
        keyword_found = detect_keyword_in_df(df, "charges", keyword)
        if keyword_found:
            keywords_found.append(keyword_found)
    if keywords_found:
        special_msg = (
            keywords_found[0]
            if len(keywords_found) == 1
            else ", " "".join(keywords_found)
        )
        logging.info(f"Keywords {keyword_list} found in CSV")
        logging.info(
            f"Updating subject line and mobile tease to include: {special_msg}"
        )
        subject_line = subject_line + f", ALERT: {special_msg}"
        mobile_tease_content = "Detected: " + special_msg
    else:
        logging.info(f"Keywords {keyword_list} not found in CSV")
    return subject_line, mobile_tease_content


def create_final_email_payload(
    dir_email_template: Union[str, object],
    mobile_tease_content: str,
    intro_content: str,
    body_content: str,
    footer_content: str,
) -> str:
    """
    This function fuses our scraped data with snippets of HTML to create our final email payload. It returns an email in MIMEtext format
    """

    logging.info("Wrapping content in HTML")

    # GET EMAIL COMPONENTS
    # First creating a list of all our email template components
    component_list = [
        "html_head",
        "html_body_top",
        "mobile_tease_top",
        "mobile_tease_bottom",
        "table_top",
        "header",
        "intro_top",
        "email_body_top",
        "footer_top",
    ]
    # Then creating a dict of all those components by reading from their respective files
    parts = {}
    for component in component_list:
        path_to_component = dir_email_template / "{}.html".format(component)
        parts[component] = path_to_component.read_text()

    ############  HTML HEAD + A BIT OF BODY TOP  #################

    # COMBINE HTML
    mobile_tease = (
        parts["mobile_tease_top"] + mobile_tease_content + parts["mobile_tease_bottom"]
    )
    html_top = (
        parts["html_head"] + parts["html_body_top"] + mobile_tease + parts["table_top"]
    )

    ############  BODY: REST OF TOP  #############################

    intro_container_bottom = "</div></td></tr>"
    intro = (
        parts["header"] + parts["intro_top"] + intro_content + intro_container_bottom
    )

    ##################### BODY: MIDDLE  ############################

    # This is where we insert our main payload. eg. scraped data.
    email_body_bottom = "</td></tr>"
    email_body = parts["email_body_top"] + body_content + email_body_bottom

    #####################  BODY: BOTTOM  #########################

    footer_bottom = "</td></tr>"
    html_bottom = "</div></center></table></body></html>"
    footer = parts["footer_top"] + footer_content + footer_bottom + html_bottom

    #########################  COMBINE  ##############################

    # JOIN IT ALL TOGETHER
    message = html_top + intro + email_body + footer

    logging.info("HTML payload generated")
    return message


def create_subject_line(
    target_scrape_date: str,
    formatted_date: str,
    yesterday_date: str,
    county_list: List[str],
) -> str:

    logging.info("Generating subject line...")

    # SET SUBJECT LINE
    if len(county_list) == 1:
        if target_scrape_date == "today":
            subject = "Criminal cases filed in {} County today - {}".format(
                county_list[0], formatted_date
            )
        elif target_scrape_date == "yesterday":
            subject = "Criminal cases filed in {} County yesterday - {}".format(
                county_list[0], yesterday_date
            )
    else:
        if target_scrape_date == "today":
            subject = "Criminal cases filed so far today - {}".format(formatted_date)
        elif target_scrape_date == "yesterday":
            subject = "Criminal cases filed yesterday - {}".format(yesterday_date)

    logging.info("Subject line generated")

    return subject


def login_to_gmail_and_send(
    recipients: List[str],
    html_msg: str,
    subject_line: str,
    attachments: Optional[List[str]] = [],
):

    """
    Takes a string (with HTML markup, if desired), converts to MIME, logs into gmail  and sends message.

    :param recipients: List of one or more email address
    :param html_msg: Str for email contents. String can include HTML.
    :param subject_line: Str.
    :param attachments: OPTIONAL. List of paths to files to attach to email.
    :return: None
    """

    # MESSAGE
    mime_msg = MIMEMultipart()
    mime_msg.attach(MIMEText(html_msg, "html"))

    # GET ENV VARIABLES - SENDER LOGIN
    sender_email_username = os.environ.get("SENDER_EMAIL_USERNAME")
    sender_email_password = os.environ.get("SENDER_EMAIL_PASSWORD")

    # SET FROM/TO/SUBJECT
    mime_msg["From"] = f"Pa Court Report <{sender_email_username}>"
    mime_msg["To"] = ", ".join(recipients)
    mime_msg["Subject"] = subject_line

    # OPTIONAL: ADD ATTACHMENTS
    if attachments:
        logging.info(f"Attaching files: {attachments}")
        for attachment_path in attachments:
            with open(attachment_path, "rb") as attachment:
                p = MIMEBase("application", "octet-stream")
                p.set_payload(attachment.read())
                encoders.encode_base64(p)
                p.add_header(
                    "Content-Disposition",
                    f"attachment; filename={attachment_path.name}",
                )
                mime_msg.attach(p)
        logging.info("files attached")

    # LOGIN AND SEND
    mime_msg = mime_msg.as_string()
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email_username, sender_email_password)
    server.sendmail(sender_email_username, recipients, mime_msg)
    server.quit()
    logging.info("Email sent!")
