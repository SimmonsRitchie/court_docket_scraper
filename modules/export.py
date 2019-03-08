"""
This module handles the conversion of docket data to JSON.

"""

from modules import misc

import pandas as pd
import json
import os
from datetime import datetime

def payload_generation(base_folder_email, base_folder_csv, create_dict, county):

    # CONVERTING DATA INTO PANDAS DATAFRAME FOR SORTING AND FORMATTING
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
    df['Bail'] = df['Bail'].apply(misc.currency_convert)


    # CREATE EMAIL PAYLOAD OR ADD DATA TO EXISTING EMAIL PAYLOAD
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


    # CREATE CSV PAYLOAD OR ADD DATA TO EXISTING CSV PAYLOAD
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
    csv_payload_path = misc.csv_payload_path_generator(base_folder_csv)
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

    # CONVERT DATAFRAME TO JSON
    print("Creating new dictionary so we can include metadata with JSON payload...")
    date_scrape = datetime.now().replace(microsecond=0).isoformat() # Metadata field: current time
    selected_counties = county_list # Metadata field: list of all counties that were SELECTED by user to be scraped
    returned_counties = df["county"].unique().tolist() # Metadata field: list of all counties RETURNED in scraped data
    cases_dict = df.to_dict(orient='records') # Data: this is our actual data from the scrape, each case will be a single object in a big array
    final_dict = {
        "scrapeDatetime": date_scrape,
        "countiesSelectedForScrape": selected_counties,
        "countiesReturnedFromScrape": returned_counties,
        "cases": cases_dict
    }
    print("New dictionary created")
    print("Exporting dictionary as JSON file...")
    with open(json_payload_path, "w") as write_file:
        json.dump(final_dict, write_file, indent=4)
    print("Export complete")