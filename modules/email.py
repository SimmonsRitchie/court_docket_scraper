"""
This module handles sending auto email. It also converts dockets into an email friendly text file.
"""

# load email modules
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta

# Load my modules
from modules import misc, export


def email_notification(
    dirs,
    paths,
    destination_email_addresses,
    sender_email_address,
    sender_email_password,
    date_and_time_of_scrape,
    target_scrape_date,
    county_list,
):

    print("Sending email...")

    # GET DATE INFO
    date_and_time_of_scrape = datetime.strptime(
        date_and_time_of_scrape, "%Y-%m-%dT%H:%M:%S"
    )  # Parse ISO date into datetime obj
    formatted_date = date_and_time_of_scrape.strftime("%a, %b %-d %Y")
    formatted_time = date_and_time_of_scrape.strftime("%-I:%M %p")
    yesterday_date = (datetime.now() - timedelta(1)).strftime("%a, %b %-d %Y")

    # GENERATE EMAIL HTML
    # We take our existing HTML payload of docket data and wrap it in more HTML to make it look nice.
    message = create_final_email_payload(
        dirs,
        paths,
        target_scrape_date,
        formatted_date,
        formatted_time,
        yesterday_date,
        county_list,
    )

    # GENERATE SUBJECT LINE
    subject = create_subject_line(
        paths, target_scrape_date, formatted_date, yesterday_date, county_list
    )

    # ACCESS GMAIL AND SEND
    message["From"] = f"Pa Court Report <{sender_email_address}>"
    message["To"] = ", ".join(destination_email_addresses)
    message["Subject"] = subject

    msg_full = message.as_string()

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email_address, sender_email_password)
    server.sendmail(sender_email_address, destination_email_addresses, msg_full)
    server.quit()
    print("Email sent!")


def create_final_email_payload(
    dirs,
    paths,
    target_scrape_date,
    formatted_date,
    formatted_time,
    yesterday_date,
    county_list,
):
    # FINAL EMAIL PAYLOAD
    # This function fuses our scraped data with snippets of HTML to create our final email payload
    print("Generating final HTML payload")

    # GET DIRS
    dir_email_template = dirs["email_template"]

    # GET PATHS
    path_payload_email = paths["payload_email"]
    path_final_email = paths["email_final"]

    # GET OUR SCRAPED DATA
    # This file has all our dataframes converted into HTML from the scrape, already wrapped in a bit of HTML.
    email_body_contents = path_payload_email.read_text()

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

    # GENERATE HIDDEN MESSAGE FOR MOBILE TEASE
    if len(county_list) == 1:
        mobile_tease_content = "Here are the latest criminal cases filed in {} County".format(
            county_list[0]
        )
    else:
        mobile_tease_content = (
            "Here are the latest criminal cases filed in central Pa. courts."
        )

    # COMBINE HTML
    mobile_tease = (
        parts["mobile_tease_top"] + mobile_tease_content + parts["mobile_tease_bottom"]
    )
    html_top = (
        parts["html_head"] + parts["html_body_top"] + mobile_tease + parts["table_top"]
    )

    #################################  BODY: REST OF TOP  ##########################################

    # GENERATE INTRO
    # we create different intros based on conditions
    if len(county_list) == 1:
        intro_header = '<span class="subheading">{} county scrape</span>'.format(
            county_list[0]
        )
        if target_scrape_date == "today":
            intro_contents = "<p>The following criminal cases were filed in {} County today as of {}.</p>\
                             <p>Check tomorrow morning's email to see all cases filed today.</p>".format(
                county_list[0], formatted_time
            )
        elif target_scrape_date == "yesterday":
            intro_contents = "<p>The following criminal cases were filed in {} County yesterday ({}).</p>\
                            ".format(
                county_list[0], yesterday_date
            )
    else:
        if target_scrape_date == "today":
            intro_header = '<span class="subheading">afternoon scrape</span>'
            intro_contents = "<p>The following criminal cases were filed in district courts today as of {}.</p>\
                             <p>Check tomorrow morning's email to see all cases filed today.</p>".format(
                formatted_time
            )
        elif target_scrape_date == "yesterday":
            intro_header = '<span class="subheading">Morning scrape</span>'
            intro_contents = "<p>The following criminal cases were filed in district courts yesterday ({}).</p>\
                        <p>You can also view a searchable list of these cases\
                        <a href='https://s3.amazonaws.com/court-dockets/index.html'>here</a>.</p>\
                    ".format(
                yesterday_date
            )

    # COMBINE HTML
    intro_container_bottom = "</div></td></tr>"
    intro = (
        parts["header"]
        + parts["intro_top"]
        + intro_header
        + intro_contents
        + intro_container_bottom
    )

    #################################  BODY: MIDDLE  ##########################################

    # GENERATE EMAIL BODY
    # Here is where we insert the HTML we generated from our scraping.
    email_body_bottom = "</td></tr>"
    email_body = parts["email_body_top"] + email_body_contents + email_body_bottom

    #################################  BODY: BOTTOM  ##########################################

    # GENERATE FOOTER
    footer_contents = "<p>This information was scraped at {} on {}</p>\
                      <p>This email was generated by a program written by Daniel Simmons-Ritchie. \
                      If you don't wish to receive these emails or you see errors in this email, contact him at \
                      <a href='mailto:simmons-ritchie@pennlive.com'>simmons-ritchie@pennlive.com</a></p>".format(
        formatted_time, formatted_date
    )

    # COMBINE HTML
    footer_bottom = "</td></tr>"
    html_bottom = "</div></center></table></body></html>"
    footer = parts["footer_top"] + footer_contents + footer_bottom + html_bottom

    #################################  COMBINE  ##########################################

    # JOIN IT ALL TOGETHER
    msg_content = html_top + intro + email_body + footer
    message = MIMEText(msg_content, "html")

    # SAVE A COPY OF FINAL EMAIL FOR TESTING AND DEBUGGING PURPOSES
    export.save_copy_of_final_email(path_final_email, msg_content)

    print("HTML payload generated")
    return message


def create_subject_line(
    paths, desired_scrape_date_literal, formatted_date, yesterday_date, county_list
):

    print("Creating subject line")

    # GET PATHS
    email_payload_path = paths["payload_email"]

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

    # APPEND HOMICIDE NOTE IF NEEDED
    # Access email body
    with open(email_payload_path, "r") as fin:
        email_body = fin.read()
    if "homicide" in email_body or "Homicide" in email_body or "HOMICIDE" in email_body:
        subject = subject + " (HOMICIDE detected)"

    print("Subject line generated")

    return subject
