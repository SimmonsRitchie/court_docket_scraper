"""
This module uploads data to a REST API.
"""
# third party or inbuilt libs
import pandas as pd
import requests
import os
import logging
import json

# project modules
from modules.misc import clean_df
from modules.email import email_error_notification
from locations import paths

ERROR_SUMMARY = "An error occurred during upload to REST API."
ABORTING_UPLOAD = "Aborting upload."


def upload_to_rest_api():

    # GET ENV VARS
    rest_api = {
        "hostname": os.getenv("REST_API_HOSTNAME"),
        "login_endpoint": os.getenv("LOGIN_END_POINT"),
        "logout_endpoint": os.getenv("LOGOUT_END_POINT"),
        "post_endpoint": os.getenv("POST_END_POINT"),
        "username": os.getenv("REST_API_USERNAME"),
        "password": os.getenv("REST_API_PASSWORD"),
    }

    # MAKING SURE ALL ENV VARS ARE SET
    for key, value in rest_api.items():
        if value is None:
            full_error = f"Missing value for key {key} in rest_api ENV variables"
            logging.error(full_error)
            email_error_notification(ERROR_SUMMARY, full_error)
            logging.error(ABORTING_UPLOAD)
            return

    logging.info(
        f"*** Uploading CSV to REST API at host: " f"{rest_api['hostname']} ***"
    )

    # GET PATH TO CSV
    csv_payload_path = paths["payload_csv"]
    logging.info("Path to CSV: {csv_payload_path}")

    # LOAD CSV + CLEAN
    logging.info("Converting CSV from file...")
    df = pd.read_csv(
        csv_payload_path, dtype={"docketnum": str, "dob": str, "filing_date": str}
    )  # this is to ensure docketnum is str
    df = clean_df(
        df
    )  # remove cases with duplicate docketnums if they exists, converts NaN and NaT to None (will
    # appear as 'null' in json sent in Post request)

    # SELECT FIELDS
    # Your API may expect certain fields and not others. Use ENV vars to
    # customize field selection. Default is to use all fields available.
    fields = os.getenv("FIELDS_FOR_UPLOAD", None)
    if fields:
        fields = json.loads(fields)
        fields = [x.lower().replace(" ", "_") for x in fields]  # cleaning
        df = df[fields]

    # CONVERT TO JSON
    logging.info("Converting CSV to JSON...")
    cases_json = df.to_dict(orient="records")
    logging.debug(cases_json)
    logging.info("CSV converted to JSON")

    # REQUESTS
    # We request three different endpoints. We abort if we encounter any HTTP errors.
    # LOGIN
    with requests.Session() as s:
        try:
            s = login(s, rest_api)
            s = add_cases(s, rest_api, cases_json)
            logout(s, rest_api)
        except Exception as full_error:
            print(full_error)
            email_error_notification(ERROR_SUMMARY, full_error)
            logging.error(ABORTING_UPLOAD)
            return

    # success
    logging.info("*** Data succesfully uploaded to {} ***".format(rest_api["hostname"]))


def login(s, rest_api):
    action = "Logging in"
    logging.info(f"{action}...")
    login_data = {"username": rest_api["username"], "password": rest_api["password"]}
    full_login_path = rest_api["hostname"] + rest_api["login_endpoint"]

    r = s.post(full_login_path, json=login_data)
    data = r.json()
    status_code = r.status_code

    # failure
    # if assert evaluates as false, raise error
    if status_code != 200:  # not status 'added successfully'
        failure_output(action, status_code, data)
        assert status_code == 200, data

    # success
    success_output(action, data)

    # update headers
    logging.info("Updating headers with JWT token")
    access_token = data["access_token"]
    s.headers.update({"Authorization": f"Bearer {access_token}"})
    return s


def add_cases(s, rest_api, json_data):
    action = "Adding cases"
    logging.info(f"{action}...")
    full_post_path = rest_api["hostname"] + rest_api["post_endpoint"]
    r = s.post(full_post_path, json=json_data)
    status_code = r.status_code
    data = r.json()

    # failure
    if status_code != 201:  # not status 'added successfully'
        failure_output(action, status_code, data)
        assert status_code == 201, data

    # success
    success_output(action)
    return s


def logout(s, rest_api):
    action = "Logging out"
    logging.info(f"{action}...")
    full_logout_path = rest_api["hostname"] + rest_api["logout_endpoint"]
    r = s.post(full_logout_path)
    status_code = r.status_code
    data = r.json()

    # failure
    if status_code != 200:  # not status 'ok'
        failure_output(action, status_code, data)
        assert status_code == 200, data

    # success
    success_output(action, data)
    return s


############ OUTPUT FUNCTIONS ####################
# Some reusable functions for displaying output from HTTP requests.


def failure_output(action, status, data):
    logging.error(f"Failed to {action}")
    logging.error(f"STATUS CODE: {status}, RESPONSE: {data}")


def success_output(action, data=None):
    logging.info(f"{action} successful")

    if data:
        logging.debug(data)
