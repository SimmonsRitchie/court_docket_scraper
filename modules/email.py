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
    base_folder_email,
    base_folder_email_template,
    base_folder_final_email,
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
    message = create_final_email_payload(
        base_folder_email,
        base_folder_email_template,
        base_folder_final_email,
        target_scrape_date,
        formatted_date,
        formatted_time,
        yesterday_date,
        county_list,
    )

    # GENERATE SUBJECT LINE
    subject = create_subject_line(
        base_folder_email,
        target_scrape_date,
        formatted_date,
        yesterday_date,
        county_list,
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
    base_folder_email,
    base_folder_email_template,
    base_folder_final_email,
    target_scrape_date,
    formatted_date,
    formatted_time,
    yesterday_date,
    county_list,
):
    # FINAL EMAIL PAYLOAD
    # This function fuses our scraped data with snippets of HTML to create our final email payload
    print("Generating final HTML payload")

    # GET PATHS OF EMAIL COMPONENTS
    # First creating a list of all our email template components
    email_components = [
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
    # Creating blank dictionary to act as a look-up table
    email_paths = {}
    # Looping over email components to create dict of paths
    for component in email_components:
        filename = component + ".html"
        path_to_item = misc.email_template_path_generator(
            base_folder_email_template, filename
        )
        email_paths[component] = path_to_item

    # GENERATE HTML HEAD AND BODY TOP
    with open(email_paths["html_head"], "r") as fin:
        html_head = fin.read()
    with open(email_paths["html_body_top"], "r") as fin:
        html_body = fin.read()

    # GENERATE HIDDEN MESSAGE FOR MOBILE TEASE
    # mobile tease top
    with open(email_paths["mobile_tease_top"], "r") as fin:
        mobile_tease_top = fin.read()
    # mobile tease content
    if len(county_list) == 1:
        mobile_tease_content = "Here are the latest criminal cases filed in {} County".format(
            county_list[0]
        )
    else:
        mobile_tease_content = (
            "Here are the latest criminal cases filed in central Pa. courts."
        )
    # mobile tease bottom + start of main email container div
    with open(email_paths["mobile_tease_bottom"], "r") as fin:
        mobile_tease_bottom = fin.read()
    mobile_tease = mobile_tease_top + mobile_tease_content + mobile_tease_bottom

    # GENERATE MAIN DIV AND MAIN TABLE
    with open(email_paths["table_top"], "r") as fin:
        table_top = fin.read()

    # COMBINE TOP HTML TOGETHER
    html_top = html_head + html_body + mobile_tease + table_top

    # GENERATE HEADER
    with open(email_paths["header"], "r") as fin:
        header = fin.read()

    # GENERATE INTRO
    # intro top
    with open(email_paths["intro_top"], "r") as fin:
        intro_container_top = fin.read()
    # intro header and contents
    # we provide different intros if only one county was chosen for scrape
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
    # intro bottom
    intro_container_bottom = "</div></td></tr>"
    # unify intro
    intro = intro_container_top + intro_header + intro_contents + intro_container_bottom

    # GENERATE EMAIL BODY
    # email body top
    with open(email_paths["email_body_top"], "r") as fin:
        email_body_top = fin.read()
    # email body contents
    email_payload_path = misc.email_payload_path_generator(base_folder_email)
    with open(email_payload_path, "r") as fin:
        email_body_contents = fin.read()
    # email body bottom
    email_body_bottom = "</td></tr>"

    # unify
    email_body = email_body_top + email_body_contents + email_body_bottom

    # GENERATE FOOTER
    # footer top
    with open(email_paths["footer_top"], "r") as fin:
        footer_top = fin.read()
    # footer contents
    footer_contents = "<p>This information was scraped at {} on {}</p>\
                      <p>This email was generated by a program written by Daniel Simmons-Ritchie. \
                      If you don't wish to receive these emails or you see errors in this email, contact him at \
                      <a href='mailto:simmons-ritchie@pennlive.com'>simmons-ritchie@pennlive.com</a></p>".format(
        formatted_time, formatted_date
    )
    # footer bottom
    footer_bottom = "</td></tr>"
    # unify
    footer = footer_top + footer_contents + footer_bottom

    # GENERATE HTML BOTTOM
    html_bottom = "</div></center></table></body></html>"

    # JOIN IT ALL TOGETHER
    msg_content = (
        html_top + mobile_tease + header + intro + email_body + footer + html_bottom
    )
    message = MIMEText(msg_content, "html")

    # SAVE A COPY OF FINAL EMAIL FOR TESTING AND DEBUGGING PURPOSES
    export.save_copy_of_final_email(base_folder_final_email, msg_content)

    print("HTML payload generated")
    return message


def create_subject_line(
    base_folder_email,
    desired_scrape_date_literal,
    formatted_date,
    yesterday_date,
    county_list,
):

    print("Creating subject line")

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
    email_payload_path = misc.email_payload_path_generator(base_folder_email)
    with open(email_payload_path, "r") as fin:
        email_body = fin.read()
    if "homicide" in email_body or "Homicide" in email_body or "HOMICIDE" in email_body:
        subject = subject + " (HOMICIDE detected)"

    print("Subject line generated")

    return subject
