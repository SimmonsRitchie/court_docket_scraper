"""
This module handles the conversion of docket data to JSON.

"""

from modules import misc, style

import pandas as pd
import json
import os
from datetime import datetime

def payload_generation(base_folder_email, base_folder_csv, data_in_dictionary_format, county):

    # CONVERTING DATA INTO PANDAS DATAFRAME FOR SORTING AND FORMATTING
    df = convert_dictionary_into_dataframe(data_in_dictionary_format, county)

    # SET STYLES FOR EMAIL PAYLOAD
    df_styled = df.style \
        .set_table_styles(style.table_style) \
        .set_table_attributes(style.table_attribs) \
        .format({'URL': style.make_clickable})

    # CREATE EMAIL PAYLOAD OR ADD DATA TO EXISTING EMAIL PAYLOAD
    email_payload_path = misc.email_payload_path_generator(base_folder_email)
    row_count = df.shape[0] # count of cases
    intro = "{} in {} County:".format(row_count, county)
    convert_dataframe_to_html(df_styled, intro, email_payload_path, include_index=False, render=True) # Set render to True if using Pandas styles

    # CREATE CSV PAYLOAD
    csv_payload_path = misc.csv_payload_path_generator(base_folder_csv)
    convert_dataframe_to_csv(df, csv_payload_path, county)


def convert_dictionary_into_dataframe(data_in_dictionary_format, county):
    print("Turning saved data on {} county dockets into Pandas dataframe".format(county))
    pd.set_option('display.max_colwidth', -1)
    df = pd.DataFrame.from_dict(data_in_dictionary_format)
    df = df[["Name", "Filing date", "DOB", "Charges", "Bail", "URL"]]
    print("Removing duplicate rows if any exist")
    df = df.drop_duplicates()
    print("Convert bail column to integer data type")
    df['Bail'] = df['Bail'].apply(pd.to_numeric, errors='coerce')
    print("Sorting dockets by bail amount, descending order")
    df = df.sort_values(by='Bail', ascending=False)
    print("Reformatting bail amount in currency format")
    df['Bail'] = df['Bail'].apply(misc.currency_convert)
    return df


def convert_dataframe_to_html(df, table_header_contents, email_payload_path,include_index, render):
    print("Saving dataframe as text file for email payload")

    if render:
        if not include_index:
            df = df.hide_index()
        html_dataframe = df.render()
    else:
        html_dataframe = df.to_html(index=include_index)

    # WRAP TABLE HEADER WITH HTML
    # table header top
    with open("email_template/table_header.html", "r") as fin:
        table_header_top = fin.read()
    # table header bottom
    table_header_bottom = "</span></div>"
    # unite
    table_header_with_html = table_header_top + table_header_contents + table_header_bottom

    # JOIN INTRO WITH BODY
    html_payload = table_header_with_html + html_dataframe

    # WRAP HTML PAYLOAD WITH DIV
    html_payload = '<div class="datatable_container">' + html_payload + '</div>'

    if os.path.exists(email_payload_path):
        with open(email_payload_path, "a") as fin:
            print("Existing text file found: Adding dataframe")
            fin.write(html_payload)
            print("Dataframe added")
    else:
        with open(email_payload_path, "w") as fout:
            print("Creating email payload text file")
            fout.write(html_payload)
            print("File created")


def convert_dataframe_to_csv(df, csv_payload_path, county):
    print("Saving dataframe as CSV file")

    print("Adding 'county' field to dataframe")
    df.insert(0, 'county', county)
    print("Added")

    print("Changing headers to lowercase and replacing spaces so export data is cleaner")
    df.columns = df.columns.str.lower().str.replace(" ","_")
    print("Headers reformatted")

    print("Converting date fields to ISO format")
    df["dob"] = pd.to_datetime(df["dob"]).dt.strftime("%Y-%m-%d")
    df["filing_date"] = pd.to_datetime(df["filing_date"]).dt.strftime("%Y-%m-%d")
    print("Dates converted")

    print("Writing CSV file...")
    if os.path.exists(csv_payload_path):
        print("Existing CSV file found")
        print("loading existing CSV as dataframe...")
        df_from_csv = pd.read_csv(csv_payload_path)
        print("Combining dataframes...")
        df_combined = pd.concat([df_from_csv, df])
        print("Saving new dataframe as CSV...")
        df_combined.to_csv(csv_payload_path, index=False)
        print("New CSV created")
    else:
        df.to_csv(csv_payload_path, index=False)
        print("CSV created")


def convert_csv_to_json(base_folder_csv, base_folder_json, county_list):
    print("Converting CSV to JSON")

    # GET PATHS
    print("Getting path names...")
    csv_payload_path = misc.csv_payload_path_generator(base_folder_csv)
    json_payload_path = misc.json_payload_path_generator(base_folder_json)
    print("Got path names")

    # CONVERT CSV TO DATAFRAME
    print("Loading CSV file as pandas dataframe...")
    df = pd.read_csv(csv_payload_path)
    print("Dataframe created")

    # CHANGE HEADERS TO CAMEL CASE
    # Doing this just to make final JSON file more javascript friendly
    print("Reformatting headers in camel case")
    df.rename(columns=lambda x: misc.camel_case_convert(x), inplace=True)
    print("Reformatted")

    # REMOVE NAN
    # If we don't remove NaNs we'll get invalid JSON
    df = df.fillna("")

    # CONVERT DATAFRAME TO JSON
    print("Creating new dictionary so we can include metadata with JSON payload...")
    date_and_time_of_scrape = datetime.now().replace(microsecond=0).isoformat() # Metadata field: current time
    selected_counties = county_list # Metadata field: list of all counties that were SELECTED by user to be scraped
    returned_counties = df["county"].unique().tolist() # Metadata field: list of all counties RETURNED in scraped data
    cases_dict = df.to_dict(orient='records') # Data: this is our actual data from the scrape, each case will be a single object in a big array
    final_dict = {
        "scrapeDatetime": date_and_time_of_scrape,
        "countiesSelectedForScrape": selected_counties,
        "countiesReturnedFromScrape": returned_counties,
        "cases": cases_dict
    }
    print("New dictionary created")
    print("Exporting dictionary as JSON file...")
    with open(json_payload_path, "w") as write_file:
        json.dump(final_dict, write_file, indent=4)
    print("Export complete")
    return date_and_time_of_scrape



