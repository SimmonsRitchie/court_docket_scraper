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

# Load my modules
from modules import export
from modules.misc import get_datetime_now_formatted
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
    mobile_tease_content = error_summary + ("&nbsp;&zwnj;" * 50)
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
    default_recipients = json.loads(os.environ.get("DESTINATION_EMAIL_ADDRESSES"))
    recipients = json.loads(
        os.environ.get("DESTINATION_EMAIL_ADDRESS_FOR_ERRORS", default_recipients)
    )

    login_to_gmail_and_send(recipients, message, subject_line, attachments)


def email_notification(
    date_and_time_of_scrape: object, target_scrape_day: str, county_list: List[str]
) -> None:

    """ Assembles and sends our email notification after successful scrape """

    logging.info("Sending email with scraped data...")

    # GET DATE INFO - NEED FOR CUSTOM MESSAGES
    date_and_time_of_scrape = datetime.strptime(
        date_and_time_of_scrape, "%Y-%m-%dT%H:%M:%S"
    )  # Parse ISO date into datetime obj
    formatted_date = date_and_time_of_scrape.strftime("%a, %b %-d %Y")
    formatted_time = date_and_time_of_scrape.strftime("%-I:%M %p")
    yesterday_date = (datetime.now() - timedelta(1)).strftime("%a, %b %-d %Y")

    # GENERATE CUSTOM MESSAGES
    mobile_tease_content = gen_mobile_tease_content(county_list)
    intro_content = gen_intro_content(
        county_list, target_scrape_day, formatted_date, yesterday_date
    )
    footer_content = gen_footer_content(formatted_time, formatted_date)
    subject_line = create_subject_line(
        target_scrape_day, formatted_date, yesterday_date, county_list
    )

    # GET SCRAPED DATA
    scraped_data_content = paths["payload_email"].read_text()

    # CHECK FOR MURDER/HOMICIDE
    # Add a special message to subject line and mobile tease if either condition is met
    subject_line, mobile_tease_content = insert_special_message(
        scraped_data_content, mobile_tease_content, subject_line
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


def gen_mobile_tease_content(county_list: List[str]) -> str:
    # GENERATE HIDDEN MESSAGE FOR MOBILE TEASE
    if len(county_list) == 1:
        mobile_tease_content = "Here are the latest criminal cases filed in {} County".format(
            county_list[0]
        )
    else:
        mobile_tease_content = (
            "Here are the latest criminal cases filed in central Pa. courts."
        )
    return mobile_tease_content + ("&nbsp;&zwnj;" * 50)


def gen_intro_content(
    county_list: List[str],
    target_scrape_day: str,
    formatted_time: str,
    yesterday_date: str,
) -> str:
    # GENERATE INTRO
    # we create different intros based on conditions
    if len(county_list) == 1:
        intro_subheading = '<span class="subheading">{} county scrape</span>'.format(
            county_list[0]
        )
        if target_scrape_day == "today":
            intro_description = "<p>The following criminal cases were filed in {} County today as of {}.</p>\
                             <p>Check tomorrow morning's email to see all cases filed today.</p>".format(
                county_list[0], formatted_time
            )
        elif target_scrape_day == "yesterday":
            intro_description = "<p>The following criminal cases were filed in {} County yesterday ({}).</p>\
                            ".format(
                county_list[0], yesterday_date
            )
    else:
        if target_scrape_day == "today":
            intro_subheading = '<span class="subheading">afternoon scrape</span>'
            intro_description = "<p>The following criminal cases were filed in district courts today as of {}.</p>\
                             <p>Check tomorrow morning's email to see all cases filed today.</p>".format(
                formatted_time
            )
        elif target_scrape_day == "yesterday":
            intro_subheading = '<span class="subheading">Morning scrape</span>'
            intro_description = "<p>The following criminal cases were filed in district courts yesterday ({}).</p>\
                        <p>You can also view a searchable list of these cases\
                        <a href='https://s3.amazonaws.com/court-dockets/index.html'>here</a>.</p>\
                    ".format(
                yesterday_date
            )
    return intro_subheading + intro_description


def gen_footer_content(formatted_time: str, formatted_date: str) -> str:
    # GENERATE FOOTER
    return "<p>This information was scraped at {} on {} from the Pa. Unified Judicial Portal. Please note that new \
        cases are not always immediately uploaded to the website. the cases listed above may not represent all cases \
        filed for the targeted date range.</p>\
        <p>This email was generated by a program written by Daniel Simmons-Ritchie. \
        If you don't wish to receive these emails or you see errors in this email, contact him at \
        <a href='mailto:simmons-ritchie@pennlive.com'>simmons-ritchie@pennlive.com</a></p>".format(
        formatted_time, formatted_date
    )


def insert_special_message(
    scraped_data_content: str, mobile_tease_content: str, subject_line: str
) -> str:
    # We first but give priority to murder if found.
    special_msg = ""
    if "homicide" in scraped_data_content.lower():
        special_msg = "HOMICIDE detected"
    if "murder" in scraped_data_content.lower():
        special_msg = "MURDER detected"
    # change subject line + mobile tease accordingly
    if special_msg:
        subject_line = subject_line + f" ({special_msg})"
        mobile_tease_content = special_msg
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

    ##########################  HTML HEAD + A BIT OF BODY TOP  ##########################################

    # COMBINE HTML
    mobile_tease = (
        parts["mobile_tease_top"] + mobile_tease_content + parts["mobile_tease_bottom"]
    )
    html_top = (
        parts["html_head"] + parts["html_body_top"] + mobile_tease + parts["table_top"]
    )

    #################################  BODY: REST OF TOP  ##########################################

    intro_container_bottom = "</div></td></tr>"
    intro = (
        parts["header"] + parts["intro_top"] + intro_content + intro_container_bottom
    )

    #################################  BODY: MIDDLE  ##########################################

    # This is where we insert our main payload. eg. scraped data.
    email_body_bottom = "</td></tr>"
    email_body = parts["email_body_top"] + body_content + email_body_bottom

    #################################  BODY: BOTTOM  ##########################################

    footer_bottom = "</td></tr>"
    html_bottom = "</div></center></table></body></html>"
    footer = parts["footer_top"] + footer_content + footer_bottom + html_bottom

    #################################  COMBINE  ##########################################

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
    logging.info(f"Attaching files: {attachments}")
    if attachments:
        for attachment_path in attachments:
            with open(attachment_path, "rb") as attachment:
                p = MIMEBase("application", "octet-stream")
                p.set_payload((attachment).read())
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
