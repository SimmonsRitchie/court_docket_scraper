"""
This module handles sending auto email. It also converts dockets into an email friendly text file.
"""

#load email modules
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta

# Load my modules
from modules import misc



def email_notification(base_folder_email, destination_email_addresses, my_email_login, date_and_time_of_scrape, desired_scrape_date_literal):

    print("Sending email...")

    # Get date info
    date_and_time_of_scrape = datetime.strptime(date_and_time_of_scrape,
                                                "%Y-%m-%dT%H:%M:%S")  # Parse ISO date into datetime obj
    formatted_date = date_and_time_of_scrape.strftime("%a, %b %-d %Y")
    formatted_time = date_and_time_of_scrape.strftime("%-I:%M %p")
    yesterday_date = (datetime.now() - timedelta(1)).strftime("%a, %b %-d %Y")

    # Change email intro and subject line accordingly
    if desired_scrape_date_literal == "today":
        intro = "<tr><td style='font-size:20px'>" \
                "<p style='margin-bottom:20px;'>The following criminal cases were filed in district courts today as of {}.</p>" \
                "</td></tr>".format(formatted_time)
        subject = "Criminal cases filed so far today - {}".format(formatted_date)
    elif desired_scrape_date_literal == "yesterday":
        intro = "<tr><td style='font-size:20px'>" \
                "<p>The following criminal cases were filed in district courts yesterday ({}).</p>" \
                "<p style='margin-bottom:20px;'>You can also view these cases online <a href='https://s3.amazonaws.com/court-dockets/index.html'>here</a>.</p>"\
                "</td></tr>".format(yesterday_date)
        subject = "Criminal cases filed yesterday - {}".format(yesterday_date)

    # Adding HTML table elements to nest content
    # Table_top and table_bottom create a big table that nests the tables from email payload
    table_top = '<table border="0">'
    email_payload_path = misc.email_payload_path_generator(base_folder_email)
    footnote = "<tr style='margin-bottom:20px;'><td>This information was scraped at {} on {}</tr></td>".format(formatted_time, formatted_date)
    outro = "<tr><td>See errors in this email? Contact Daniel Simmons-Ritchie at simmons-ritchie@pennlive.com</tr></td>"
    table_bottom = "</table>"

    with open(email_payload_path, "r") as fin:
        email_payload = fin.read()

    msg_content = table_top + intro + email_payload + footnote + outro + table_bottom
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