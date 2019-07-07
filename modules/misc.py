"""
This module stores small, reusable functions used by several other modules.

Those functions include: getting dates, formatting dates, creating directory and file paths

"""

from datetime import datetime, timedelta
import os


def pdf_path_generator(base_folder_pdfs, docket_num):
    filename = "docket_{}.pdf".format(docket_num)
    check_directory_exists(base_folder_pdfs)
    pdf_path = os.path.join(base_folder_pdfs, filename)
    return pdf_path


def extracted_text_path_generator(base_folder_text, docketnum):
    check_directory_exists(base_folder_text)
    log_path = os.path.join(base_folder_text, "log_{}.txt".format(docketnum))
    return log_path


def email_payload_path_generator(base_folder_email):
    check_directory_exists(base_folder_email)
    yesterday = yesterday_date()
    email_filename = "email_{}.txt".format(yesterday)
    email_payload_path = os.path.join(base_folder_email, email_filename)
    return email_payload_path


def json_payload_path_generator(base_folder_json):
    check_directory_exists(base_folder_json)
    json_filename = "dockets.json"
    json_payload_path = os.path.join(base_folder_json, json_filename)
    return json_payload_path


def csv_payload_path_generator(base_folder_csv):
    check_directory_exists(base_folder_csv)
    csv_filename = "dockets.csv"
    csv_payload_path = os.path.join(base_folder_csv, csv_filename)
    return csv_payload_path


def email_template_path_generator(base_folder_email_template, filename):
    return os.path.join(base_folder_email_template, filename)


def final_email_path_generator(base_folder_final_email):
    check_directory_exists(base_folder_final_email)
    final_email_filename = "email.html"
    final_email_path = os.path.join(base_folder_final_email, final_email_filename)
    return final_email_path


def check_directory_exists(base_folder):
    directory = os.path.dirname(base_folder)
    if not os.path.exists(directory):
        os.makedirs(directory)


def yesterday_date():
    yesterday = datetime.now() - timedelta(1)
    return yesterday.strftime("%m%d%Y")


def today_date():
    today = datetime.now()
    return today.strftime("%m%d%Y")


def formatted_yesterday_date():
    yesterday = datetime.now() - timedelta(1)
    return yesterday.strftime("%m/%d/%Y")


def formatted_yesterday_date_name():
    yesterday = datetime.now() - timedelta(1)
    yesterday = yesterday.strftime("%a, %b %-d %Y")
    return yesterday


def currency_convert(x):
    if str(x) == "nan":
        x = ""
        return x
    elif type(x) == float or type(x) == int:
        x = "${:,.0f}".format(x)
        return x
    else:
        return ""


def camel_case_convert(item):
    item = (
        item.title().replace(" ", "").replace("_", "").replace("-", "")
    )  # removing all '_', '-', and spaces
    item = item[0].lower() + item[1:] if item else ""
    return item
