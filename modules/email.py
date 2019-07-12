"""
This module handles sending auto email. It also converts dockets into an email friendly text file.
"""

# load email modules
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import os
import json

# Load my modules
from modules import export
from modules.misc import get_datetime_now_formatted
from locations import test_dirs, test_paths


def email_error_notification(error_summary, full_error_msg):
    error_emails_enabled = False if os.environ.get("ERROR_EMAILS") == "FALSE" else True
    if not error_emails_enabled:
        print("Email error notifications are disabled\nNo error email will be sent")
        return

    print("Sending error notification to desiginated email addresses")

    # GET INFO FOR MESSAGE
    error_datetime = get_datetime_now_formatted()
    dir_email_template = test_dirs["email_template"]
    county_list = [
        x.title() for x in json.loads(os.environ.get("COUNTY_LIST"))
    ]  # Counties are transformed into title case
    target_scrape_day = os.environ.get("TARGET_SCRAPE_DATE", "yesterday").lower()


    mobile_tease_content = error_summary
    intro_content = f"<p>Something went wrong during scrape of {target_scrape_day}'s cases for following counties:"\
    f"{county_list}.<p>"\
    f"<p>Summary: {error_summary}.</p>" \
    f"<p>Error time: {error_datetime}.</p>"
    body_content = f"<p>Full error message:</p><p>{full_error_msg}</p>"
    footer_content = ""
    subject_line = "ERROR: something went wrong"

    # ATTACH CSV
    # TODO: Add attachment

    # CREATE HTML PAYLOAD
    message = create_final_email_payload(
        dir_email_template,
        mobile_tease_content,
        intro_content,
        body_content,
        footer_content
    )

    # SEND
    default_recipients = json.loads(
        os.environ.get("DESTINATION_EMAIL_ADDRESSES")
    )
    recipients = json.loads(
        os.environ.get("DESTINATION_EMAIL_ADDRESS_FOR_ERRORS", default_recipients)
    )

    login_to_gmail_and_send(recipients, message,subject_line)


def email_notification(
    date_and_time_of_scrape,
    target_scrape_day,
    county_list
):

    print("Sending email...")

    # GET DATE INFO - NEED FOR CUSTOM MESSAGES
    date_and_time_of_scrape = datetime.strptime(
        date_and_time_of_scrape, "%Y-%m-%dT%H:%M:%S"
    )  # Parse ISO date into datetime obj
    formatted_date = date_and_time_of_scrape.strftime("%a, %b %-d %Y")
    formatted_time = date_and_time_of_scrape.strftime("%-I:%M %p")
    yesterday_date = (datetime.now() - timedelta(1)).strftime("%a, %b %-d %Y")

    # GENERATE CUSTOM MESSAGES
    mobile_tease_content = gen_mobile_tease_content(county_list)
    intro_content = gen_intro_content(county_list, target_scrape_day, formatted_date, yesterday_date)
    footer_content = gen_footer_content(formatted_time, formatted_date)
    subject_line = create_subject_line(
        target_scrape_day, formatted_date, yesterday_date, county_list
    )


    # GET SCRAPED DATA
    scraped_data_content = test_paths["payload_email"].read_text()

    # CHECK FOR MURDER/HOMICIDE
    # Add a special message to subject line and mobile tease if either condition is met
    subject_line, mobile_tease_content = insert_special_message(scraped_data_content, mobile_tease_content,
                                                                subject_line)
    # GENERATE EMAIL HTML
    # We take our HTML payload of docket data and wrap it in more HTML to make it look nice.
    message = create_final_email_payload(
        test_dirs["email_template"],
        mobile_tease_content,
        intro_content,
        scraped_data_content,
        footer_content
    )

    # SAVE EMAIL HTML - FOR DEBUGGING PURPOSES
    export.save_copy_of_final_email(test_paths["email_final"], message)

    # ACCESS GMAIL AND SEND
    recipients = json.loads(
        os.environ.get("DESTINATION_EMAIL_ADDRESSES")
    )
    login_to_gmail_and_send(recipients, message, subject_line)


def gen_mobile_tease_content(county_list):
    # GENERATE HIDDEN MESSAGE FOR MOBILE TEASE
    if len(county_list) == 1:
        return "Here are the latest criminal cases filed in {} County".format(
            county_list[0]
        )
    else:
        return (
            "Here are the latest criminal cases filed in central Pa. courts."
        )

def gen_intro_content(county_list, target_scrape_day, formatted_time, yesterday_date):
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


def gen_footer_content(formatted_time, formatted_date):
    # GENERATE FOOTER
    return "<p>This information was scraped at {} on {}</p>\
                      <p>This email was generated by a program written by Daniel Simmons-Ritchie. \
                      If you don't wish to receive these emails or you see errors in this email, contact him at \
                      <a href='mailto:simmons-ritchie@pennlive.com'>simmons-ritchie@pennlive.com</a></p>".format(
        formatted_time, formatted_date
    )


def insert_special_message(scraped_data_content, mobile_tease_content, subject_line):
    # We check for homicide first but give priority to murder if found.
    special_msg = ""
    if "homicide" in scraped_data_content.lower():
        special_msg = "HOMICIDE detected"
    if "murder" in scraped_data_content.lower():
        special_msg = "MURDER detected"
    subject_line = subject_line + " --" + special_msg
    mobile_tease_content = special_msg if special_msg else mobile_tease_content
    return subject_line, mobile_tease_content


def create_final_email_payload(
    dir_email_template,
    mobile_tease_content,
    intro_content,
    body_content,
    footer_content
):
    """
    This function fuses our scraped data with snippets of HTML to create our final email payload. It returns an email in MIMEtext format
    """

    print("Generating final HTML payload")

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
        parts["header"]
        + parts["intro_top"]
        + intro_content
        + intro_container_bottom
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

    print("final HTML payload generated")
    return message


def create_subject_line(
    desired_scrape_date_literal, formatted_date, yesterday_date, county_list
):

    print("Generating subject line")

    # SET SUBJECT LINE
    if len(county_list) == 1:
        if desired_scrape_date_literal == "today":
            subject = "Criminal cases filed in {} County today - {}".format(
                county_list[0], formatted_date
            )
        elif desired_scrape_date_literal == "yesterday":
            subject = "Criminal cases filed in {} County yesterday - {}".format(
                county_list[0], yesterday_date
            )
    else:
        if desired_scrape_date_literal == "today":
            subject = "Criminal cases filed so far today - {}".format(formatted_date)
        elif desired_scrape_date_literal == "yesterday":
            subject = "Criminal cases filed yesterday - {}".format(yesterday_date)

    print("Subject line generated")

    return subject



def login_to_gmail_and_send(recipients, message, subject_line):

    """
    Takes a string (with HTML markup, if desired), converts to MIME, logs into gmail  and sends message.

    :param recipients: List of one or more email address
    :param message: Str
    :param subject_line: Str.
    :return: None
    """

    # MESSAGE
    mime_message = MIMEText(message, "html")

    # GET ENV VARIABLES - SENDER LOGIN
    sender_email_username = os.environ.get("SENDER_EMAIL_USERNAME")
    sender_email_password = os.environ.get("SENDER_EMAIL_PASSWORD")

    # LOGIN AND SEND
    mime_message["From"] = f"Pa Court Report <{sender_email_username}>"
    mime_message["To"] = ", ".join(recipients)
    mime_message["Subject"] = subject_line

    msg_full = mime_message.as_string()

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email_username, sender_email_password)
    server.sendmail(sender_email_username, recipients, msg_full)
    server.quit()
    print("Email sent!")