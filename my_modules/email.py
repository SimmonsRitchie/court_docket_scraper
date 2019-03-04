"""
This module handles sending auto email. It also converts dockets into an email friendly text file.
"""

#load email modules
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


#Load other modules
import pandas as pd
import os

# Load my modules
from my_modules import misc


def email_payload(base_folder_email, create_dict, county):
    print("Turning saved data on {} county dockets into Pandas dataframe".format(county))
    pd.set_option('display.max_colwidth', -1)
    df = pd.DataFrame.from_dict(create_dict)
    df = df[["Name", "Filing date", "DOB", "Charges", "Bail", "URL"]]
    print("Removing duplicate rows if any exist")
    df = df.drop_duplicates()
    print("Convert bail column to integer data type")
    df['Bail'] = df['Bail'].apply(pd.to_numeric, errors='coerce')
    print("Sorting dockets by bail amount, descending order")
    df = df.sort_values(by='Bail', ascending=False)
    print("Reformatting bail amount in currency format")
    df['Bail'] = df['Bail'].apply(currency_convert)
    print("Saving dataframe as text file for email payload")
    row_count = df.shape[0]
    html = df.to_html(index=False)
    intro = "<tr><td><p style='font-size:20px'>{} in {} County:</p></td></tr>".format(row_count, county)
    new_county = intro + "<tr><td>" + html + "</td></tr>"
    email_payload_path = misc.email_payload_path_generator(base_folder_email)
    if os.path.exists(email_payload_path):
        with open(email_payload_path, "a") as fin:
            print("Existing text file found: Adding dataframe")
            fin.write(new_county)
            print("Dataframe added")
    else:
        with open(email_payload_path, "w") as fout:
            print("Creating email payload text file")
            fout.write(new_county)
            print("File created")


def currency_convert(x):
    if str(x) == "nan":
        x = ""
        return x
    elif type(x) == float or type(x) == int:
        x = '${:,.0f}'.format(x)
        return x
    else:
        return ""


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