"""
This module handles the conversion of docket data to JSON.

"""

from modules import misc

import pandas as pd
import json
import os
from datetime import datetime

def payload_generation(base_folder_email, base_folder_csv, create_dict, county):
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
    df.insert(0, 'County', county)
    print("Converting date fields to ISO format")
    df["DOB"] = pd.to_datetime(df["DOB"]).dt.strftime("%Y-%m-%d")
    df["Filing date"] = pd.to_datetime(df["Filing date"]).dt.strftime("%Y-%m-%d")
    print("Dates converted")
    print("Writing file...")
    csv_payload_path = misc.csv_payload_path_generator(base_folder_csv)
    if os.path.exists(csv_payload_path):
        print("Existing csv file found")
        print("loading existing csv as dataframe...")
        df_from_csv = pd.read_csv(csv_payload_path)
        print("Combining dataframes...")
        df_combined = pd.concat([df_from_csv, df])
        print("Saving new dataframe as csv...")
        df_combined.to_csv(csv_payload_path, index=False)
        print("New csv created")
    else:
        df.to_csv(csv_payload_path, index=False)
        print("csv created")


def currency_convert(x):
    if str(x) == "nan":
        x = ""
        return x
    elif type(x) == float or type(x) == int:
        x = '${:,.0f}'.format(x)
        return x
    else:
        return ""


def convert_csv_to_json(base_folder_csv, base_folder_json):
    print("Converting csv to JSON")
    print("Getting path names...")
    csv_payload_path = misc.csv_payload_path_generator(base_folder_csv)
    json_payload_path = misc.json_payload_path_generator(base_folder_json)
    print("Got path names")
    print("Loading CSV file as pandas dataframe...")
    df = pd.read_csv(csv_payload_path)
    print("Dataframe created")
    print("Creating new dictionary to append metadata to JSON payload...")
    cases_dict = df.to_dict(orient='records') # This is our actual data from the scrape
    county_list = df["County"].unique().tolist() # Creating metadata field: list of all counties we scraped
    date_scrape = datetime.now().replace(microsecond=0).isoformat() # Creating metadata field: current time
    final_dict = {
        "date-scrape": date_scrape,
        "county_list": county_list,
        "cases": cases_dict
    }
    print("New dictionary created")
    print("Exporting dictionary as JSON file...")
    with open(json_payload_path, "w") as write_file:
        json.dump(final_dict, write_file, indent=4)
    print("Export complete")