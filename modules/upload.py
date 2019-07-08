"""
This module uploads data to a REST API.
"""
# third party or inbuilt libs
import pandas as pd
import requests
import pprint as pp

# project modules
from modules.misc import csv_payload_path_generator


def upload_to_rest_api(rest_api, base_folder_csv):

    print(
        "\n ---------------------------------------------------------------------------------------------"
    )
    print("       UPLOADING DATA TO REST API: {}     ".format(rest_api["hostname"]))
    print(
        "\n ---------------------------------------------------------------------------------------------"
    )

    # CONVERT CSV TO JSON
    print("Converting data to json...")
    csv_payload_path = csv_payload_path_generator(base_folder_csv)
    df = pd.read_csv(csv_payload_path)
    cases_json = df.to_dict(orient="records")
    print("data converted")

    # START REQUEST SESSION
    # Request session allows us to update our request headers with JWT token after login
    s = requests.Session()

    # REQUESTS
    # We request three different endpoints. We abort if we encounter any HTTP errors.
    # LOGIN
    try:
        s = login(s, rest_api)
    except AssertionError as error:
        print(error)
        terminate_upload()
        return

    # POST
    try:
        s = add_cases(s, rest_api, cases_json)
    except AssertionError as error:
        print(error)
        terminate_upload()
        return

    # LOGOUT
    try:
        logout(s, rest_api)
    except AssertionError as error:
        print(error)
        terminate_upload()
        return


def login(s, rest_api):
    action = "Logging in"
    print(f"{action}...")
    login_data = {"username": rest_api["username"], "password": rest_api["password"]}
    full_login_path = rest_api["hostname"] + rest_api["login_endpoint"]

    r = s.post(full_login_path, json=login_data)
    data = r.json()
    status_code = r.status_code

    # failure
    # if assert evaluates as false, raise error
    if status_code != 200:  # not status 'added successfully'
        failure_output(action, status_code, data)
        assert status_code == 200, f"{action} FAILED"

    # success
    success_output(action, data)

    # update headers
    access_token = data["access_token"]
    s.headers.update({"Authorization": f"Bearer {access_token}"})
    return s


def add_cases(s, rest_api, json_data):
    action = "Adding cases"
    print(f"{action}...")
    full_post_path = rest_api["hostname"] + rest_api["post_endpoint"]
    r = s.post(full_post_path, json=json_data)
    status_code = r.status_code
    data = r.json()

    # failure
    if status_code != 201:  # not status 'added successfully'
        failure_output(action, status_code, data)
        assert status_code == 201, f"{action} FAILED"

    # success
    success_output(action, data)
    return s


def logout(base_url, s):
    action = "Logging out"
    print(f"{action}...")
    r = s.post(base_url + "/logout")
    status_code = r.status_code
    data = r.json()

    # failure
    if status_code != 200:  # not status 'ok'
        failure_output(action, status_code, data)
        assert status_code == 200, f"{action} FAILED"

    # success
    success_output(action, data)
    return s


############ OUTPUT FUNCTIONS ####################
# Some reusable functions for displaying output from HTTP requests.


def failure_output(action, status, data):
    print(f"ERROR: {action}")
    print(f"STATUS CODE: {status}")
    print("RESPONSE:")
    print(data)


def success_output(action, data=None):
    print(f"{action} successful")

    if data:
        print("RESPONSE:")
        pp.pprint(data)


def terminate_upload():
    print("--------------------- TERMINATING UPLOAD -----------------------\n")
