"""
This module handles sending auto email. It also converts dockets into an email friendly text file.
"""

#load email modules
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta

# Load my modules
from modules import misc



def email_notification(base_folder_email, destination_email_addresses, my_email_login,
                       date_and_time_of_scrape, desired_scrape_date_literal, county_list):

    print("Sending email...")

    # GET DATE INFO
    date_and_time_of_scrape = datetime.strptime(date_and_time_of_scrape,
                                                "%Y-%m-%dT%H:%M:%S")  # Parse ISO date into datetime obj
    formatted_date = date_and_time_of_scrape.strftime("%a, %b %-d %Y")
    formatted_time = date_and_time_of_scrape.strftime("%-I:%M %p")
    yesterday_date = (datetime.now() - timedelta(1)).strftime("%a, %b %-d %Y")

    # GENERATE EMAIL HTML
    message = create_final_email_payload(base_folder_email, desired_scrape_date_literal, formatted_date,
                                         formatted_time, yesterday_date, county_list)

    # GENERATE SUBJECT LINE
    subject = create_subject_line(base_folder_email, desired_scrape_date_literal, formatted_date, yesterday_date, county_list)

    # ACCESS GMAIL AND SEND
    fromaddr = "dsr.newsalert@gmail.com"
    recipients = destination_email_addresses
    message['From'] = "Pa Court Report <dsr.newsalert@gmail.com>"
    message['To'] = ", ".join(recipients)
    message['Subject'] = subject

    msg_full = message.as_string()

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(my_email_login["username"], my_email_login["pass"])
    server.sendmail(fromaddr, recipients, msg_full)
    server.quit()
    print("Email sent!")


def create_final_email_payload(base_folder_email, desired_scrape_date_literal, formatted_date, formatted_time,
                               yesterday_date, county_list):

    print("Generating final HTML payload")

    # GENERATE HTML HEAD AND BODY TOP
    with open("email_template/html_head.html", "r") as fin:
        html_head = fin.read()
    with open("email_template/html_body_top.html", "r") as fin:
        html_body = fin.read()

    # GENERATE HIDDEN MESSAGE FOR MOBILE TEASE
    # mobile tease top
    with open("email_template/mobile_tease_top.html", "r") as fin:
        mobile_tease_top = fin.read()
    # mobile tease content
    if len(county_list) == 1:
        mobile_tease_content = "Here are the latest criminal cases filed in {} County".format(county_list[0])
    else:
        mobile_tease_content = "Here are the latest criminal cases filed in central Pa. courts."
    # mobile tease bottom + start of main email container div
    with open("email_template/mobile_tease_bottom.html", "r") as fin:
        mobile_tease_bottom = fin.read()
    mobile_tease = mobile_tease_top + mobile_tease_content + mobile_tease_bottom

    # GENERATE MAIN DIV AND MAIN TABLE
    with open("email_template/table_top.html", "r") as fin:
        table_top = fin.read()

    # COMBINE TOP HTML TOGETHER
    html_top = html_head + html_body + mobile_tease + table_top

    # GENERATE HEADER
    with open("email_template/header.html", "r") as fin:
        header = fin.read()

    # GENERATE INTRO
    # intro top
    with open("email_template/intro_top.html", "r") as fin:
        intro_container_top = fin.read()
    # intro header and contents
    # we provide different intros if only one county was chosen for scrape
    if len(county_list) == 1:
        intro_header = '<span class="subheading">{} county scrape</span>'.format(county_list[0])
        if desired_scrape_date_literal == "today":
            intro_contents = "<p>The following criminal cases were filed in {} County today as of {}.</p>\
                             <p>Check tomorrow morning's email to see all cases filed today.</p>".format(county_list[0],formatted_time)
        elif desired_scrape_date_literal == "yesterday":
            intro_contents = "<p>The following criminal cases were filed in {} County yesterday ({}).</p>\
                            ".format(county_list[0], yesterday_date)
    else:
        if desired_scrape_date_literal == "today":
            intro_header = '<span class="subheading">afternoon scrape</span>'
            intro_contents = "<p>The following criminal cases were filed in district courts today as of {}.</p>\
                             <p>Check tomorrow morning's email to see all cases filed today.</p>".format(formatted_time)
        elif desired_scrape_date_literal == "yesterday":
            intro_header = '<span class="subheading">Morning scrape</span>'
            intro_contents = "<p>The following criminal cases were filed in district courts yesterday ({}).</p>\
                        <p>You can also view a searchable list of these cases\
                        <a href='https://s3.amazonaws.com/court-dockets/index.html'>here</a>.</p>\
                    ".format(yesterday_date)
    # intro bottom
    intro_container_bottom = '</div></td></tr>'
    # unify intro
    intro = intro_container_top + intro_header + intro_contents + intro_container_bottom

    # GENERATE EMAIL BODY
    # email body top
    with open("email_template/email_body_top.html", "r") as fin:
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
    with open("email_template/footer_top.html", "r") as fin:
        footer_top = fin.read()
    # footer contents
    footer_contents = "<p>This information was scraped at {} on {}</p>\
                      <p>This email was generated by a program written by Daniel Simmons-Ritchie. \
                      If you don't wish to receive these emails or you see errors in this email, contact him at \
                      <a href='mailto:simmons-ritchie@pennlive.com'>simmons-ritchie@pennlive.com</a></p>".format(
        formatted_time, formatted_date)
    # footer bottom
    footer_bottom = "</td></tr>"
    # unify
    footer = footer_top + footer_contents + footer_bottom

    # GENERATE HTML BOTTOM
    html_bottom = "</div></center></table></body></html>"

    # JOIN IT ALL TOGETHER
    msg_content = html_top + mobile_tease + header + intro + email_body + footer + html_bottom
    message = MIMEText(msg_content, 'html')

    print("HTML payload generated")
    return message



def create_subject_line(base_folder_email, desired_scrape_date_literal, formatted_date, yesterday_date, county_list):

    print("Creating subject line")

    # SET SUBJECT LINE
    if len(county_list) == 1:
        if desired_scrape_date_literal == "today":
            subject = "Criminal cases filed in {} County today - {}".format(county_list[0], formatted_date)
        elif desired_scrape_date_literal == "yesterday":
            subject = "Criminal cases filed in {} County yesterday - {}".format(county_list[0], yesterday_date)
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

