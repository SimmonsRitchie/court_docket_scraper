"""
This module handles sending auto email. It also converts dockets into an email friendly text file.
"""

#load email modules
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta

# Load my modules
from modules import misc



def email_notification(base_folder_email, destination_email_addresses, my_email_login, date_and_time_of_scrape, desired_scrape_date, desired_scrape_date_literal):

    print("Sending email...")

    # Change email intro and subject line accordingly
    if desired_scrape_date_literal == "today":
        # Get date info
        date_and_time_of_scrape = datetime.strptime(date_and_time_of_scrape,"%Y-%m-%dT%H:%M:%S")  # Parse ISO date into datetime obj
        formatted_date = date_and_time_of_scrape.strftime("%-m/%-d/%y")
        formatted_time = date_and_time_of_scrape.strftime("%-I:%M %p")
        # Intro
        intro = "<tr><td style='font-size:20px'>" \
                "<p>The following criminal cases were filed in district courts today as of {}.</p>" \
                "</td></tr>".format(formatted_time)
        # Subject
        subject = "Court dockets filed today - {}".format(formatted_date)
    elif desired_scrape_date_literal == "yesterday":
        yesterday_date = misc.yesterday_date()
        intro = "<tr><td style='font-size:20px'>" \
                "<p>The following criminal cases were filed in district courts yesterday ({}).</p>" \
                "<p style='margin-bottom:20px;'>You can also view these cases online <a href='https://s3.amazonaws.com/court-dockets/index.html'>here</a>.</p>"\
                "</td></tr>".format(yesterday_date)
        subject = "Court dockets filed yesterday - {}".format(yesterday_date)

    # Adding HTML table elements to nest content
    # Table_top and table_bottom create a big table that nests the tables from email payload
    # This was used after encountering weird issues where tables overlapped in email
    table_top = '<table border="0">'
    email_payload_path = misc.email_payload_path_generator(base_folder_email)
    outro = "<tr><td>See errors in this email? Contact simmons-ritchie@pennlive.com</tr></td>"
    table_bottom = "</table>"

    with open(email_payload_path, "r") as fin:
        email_payload = fin.read()

    msg_content = table_top + intro + email_payload + outro + table_bottom
    message = MIMEText(msg_content, 'html')

    if "homicide" in email_payload or "Homicide" in email_payload or "HOMICIDE" in email_payload:
        subject = subject + " (HOMICIDE detected)"

    fromaddr = "dsr.newsalert@gmail.com"
    recipients = destination_email_addresses
    message['From'] = 'NewsAlert <dsr.newsalert@gmail.com>'
    message['To'] = ", ".join(recipients)
    message['Subject'] = subject

    msg_full = message.as_string()

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(my_email_login["username"], my_email_login["pass"])
    server.sendmail(fromaddr, recipients, msg_full)
    server.quit()
    print("Email sent!")