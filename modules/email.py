"""
This module handles sending auto email. It also converts dockets into an email friendly text file.
"""

#load email modules
import smtplib
from email.mime.text import MIMEText

# Load my modules
from modules import misc



def email_notification(base_folder_email, email_list, login_info):
    yesterday = misc.formatted_yesterday_date_name()

    print("Sending email...")


    #Table_top and table_bottom create a big table that nests the tables from email payload
    #This was used after encountering weird issues where tables overlapped in email
    table_top = '<table border="0">'
    intro = "<tr><td><p style='font-size:20px'>The following criminal dockets were filed in district courts yesterday.</p>"
    email_payload_path = misc.email_payload_path_generator(base_folder_email)
    outro = "<tr><td>See errors in this email? Contact simmons-ritchie@pennlive.com</tr></td>"
    table_bottom = "</table>"

    with open(email_payload_path, "r") as fin:
        email_payload = fin.read()

    msg_content = table_top + intro + email_payload + outro + table_bottom
    message = MIMEText(msg_content, 'html')

    subject = "Court dockets - {}".format(yesterday)
    if "homicide" in email_payload or "Homicide" in email_payload or "HOMICIDE" in email_payload:
        subject = subject + " (HOMICIDE detected)"

    fromaddr = "dsr.newsalert@gmail.com"
    recipients = email_list
    message['From'] = 'NewsAlert <dsr.newsalert@gmail.com>'
    message['To'] = ", ".join(recipients)
    message['Subject'] = subject

    msg_full = message.as_string()

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(login_info["username"], login_info["pass"])
    server.sendmail(fromaddr, recipients, msg_full)
    server.quit()
    print("Email sent!")