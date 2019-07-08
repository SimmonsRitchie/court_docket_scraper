"""
This module handles the conversion of docket data to JSON.

"""

# inbuilt or third party libs
import pandas as pd
import json
import os
from datetime import datetime

# project modules
from modules import misc, style


def convert_dict_into_df(docketlist, county):
    # SET PANDAS OPTIONS FOR PRINT DISPLAY
    pd.set_option("display.max_columns", 20)
    pd.set_option("display.width", 2000)
    pd.set_option("display.max_rows", 700)

    # CONVERT TO DF
    print(
        "Turning saved data on {} county dockets into Pandas dataframe".format(county)
    )
    pd.set_option("display.max_colwidth", -1)
    df = pd.DataFrame(docketlist)
    print("Removing duplicate rows if any exist")
    df = df.drop_duplicates()
    if not df.empty:  # this is to avoid pandas error if df is empty
        print("Convert bail column to integer type")
        df["bail"] = df["bail"].apply(pd.to_numeric, errors="coerce")
        print(df)
    return df


def convert_df_to_html(df):

    """
    Takes a Pandas DF, reformats slightly, returns a DF rendered in HTML.
    """

    # SORTING DATA
    # Ordering by bail because cases with high bail amounts are likely to be serious crimes.
    print("Sorting dockets by bail amount, descending order")
    df = df.sort_values(by="bail", ascending=False)

    # CULLING COLUMNS + REORDERING
    # Removing columns that aren't useful, like docket_num and county
    df = df[["case_caption", "filing_date", "dob", "charges", "bail", "url"]]

    # REDUCE SIZE OF CHARGES COL
    # Charges can be particularly long so trimming it for readability in email
    df["charges"] = df["charges"].str.slice(0, 100)
    # REFORMAT COLUMN HEADS
    df.rename(index=str, columns={"case_caption": "case"}, inplace=True)
    df.columns = df.columns.str.replace(
        "_", " "
    )  # removing underscores for more human-readable format

    # SET STYLES FOR EMAIL PAYLOAD
    df_styled = (
        df.style.set_table_styles(style.table_style)
        .set_table_attributes(style.table_attribs)
        .format({"url": style.make_clickable, "bail": style.currency_convert})
    )

    # RENDER DATAFRAME AS HTML
    df_styled = df_styled.hide_index()
    return df_styled.render()


def save_html_county_payload(
    county_intro, base_folder_email, base_folder_email_template, html_dataframe=""
):

    """
    Here we take our df of county dockets rendered in HTML, add county_intro above it, wrap it an HTML table,
    and then wrap it in a div. We then save it.

    If there is an existing HTML payload file in the project directory, we'll append this county to it.

    If no dataframe is supplied, we'll replace it with an empty string. The county payload will be empty except for the
    county_intro.
    """

    print("Saving dataframe as text file for email payload")

    # GET PAYLOAD PATH
    email_payload_path = misc.email_payload_path_generator(base_folder_email)

    # CREATE TOP OF TABLE
    # table header top
    table_header_path = misc.email_template_path_generator(
        base_folder_email_template, "table_header.html"
    )
    with open(table_header_path, "r") as fin:
        table_header_top = fin.read()
    # table header bottom
    table_header_bottom = "</span></div>"
    # unite
    table_header_with_html = table_header_top + county_intro + table_header_bottom

    # JOIN INTRO WITH BODY
    html_payload = table_header_with_html + html_dataframe

    # WRAP HTML PAYLOAD WITH DIV
    html_payload = '<div class="datatable_container">' + html_payload + "</div>"

    if os.path.exists(email_payload_path):
        with open(email_payload_path, "a") as fin:
            print("Existing file found: Adding newly-created HTML to payload")
            fin.write(html_payload)
            print("Dataframe added")
    else:
        with open(email_payload_path, "w") as fout:
            print("No existing file found: Creating email payload file")
            fout.write(html_payload)
            print("File created")


def convert_df_to_csv(df, base_folder_csv):

    print("Saving dataframe as CSV file")

    # CREATE PATH
    csv_payload_path = misc.csv_payload_path_generator(base_folder_csv)

    # REFORMAT
    print(
        "Changing headers to lowercase and replacing any spaces with underscore so export data is cleaner"
    )
    df.columns = df.columns.str.lower().str.replace(" ", "_")
    print("Headers reformatted")
    print("Converting date fields to ISO format")
    df["dob"] = pd.to_datetime(df["dob"]).dt.strftime("%Y-%m-%d")
    df["filing_date"] = pd.to_datetime(df["filing_date"]).dt.strftime("%Y-%m-%d")
    print("Dates converted")

    # WRITE
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

    """
    We transform our CSV into JSON and add a few extra fields of meta data. Returned JSON uses camelcase instead of
    python snake case.
    """

    print("Converting CSV to JSON")

    # GET PATHS
    print("Getting path names...")
    csv_payload_path = misc.csv_payload_path_generator(base_folder_csv)
    json_payload_path = misc.json_payload_path_generator(base_folder_json)
    print("Got path names")

    # GENERATE METADATA FOR JSON OUTPUT
    date_and_time_of_scrape = (
        datetime.now().replace(microsecond=0).isoformat()
    )  # Metadata field: current time
    selected_counties = (
        county_list
    )  # Metadata field: list of all counties that were SELECTED by user to be scraped

    # CONVERT CSV TO DATAFRAME
    print("Loading CSV file as pandas dataframe...")

    if os.path.exists(csv_payload_path):

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

        # ADD METADATA FIELD
        returned_counties = (
            df["county"].unique().tolist()
        )  # Metadata field: list of all counties RETURNED in scraped data

        # CONVERT DF TO DICT
        cases_dict = df.to_dict(
            orient="records"
        )  # Data: this is our actual data from the scrape, each case will be a single object in a big array
    else:
        print("No CSV found - assuming no cases returned from scrape")

        # RETURN EMPTY DICT
        cases_dict = ""

        # ADD METADATA FIELD
        returned_counties = "none"

    # GENERATE JSON
    print("Creating new dictionary so we can include metadata with JSON payload...")
    final_dict = {
        "scrapeDatetime": date_and_time_of_scrape,
        "countiesSelectedForScrape": selected_counties,
        "countiesReturnedFromScrape": returned_counties,
        "cases": cases_dict,
    }
    print("New dictionary created")
    print("Exporting dictionary as JSON file...")

    with open(json_payload_path, "w") as write_file:
        json.dump(final_dict, write_file, indent=4)
    print("Export complete")
    return date_and_time_of_scrape


def save_copy_of_final_email(base_folder_final_email, msg_content):
    final_email_path = misc.final_email_path_generator(base_folder_final_email)
    with open(final_email_path, "w") as fout:
        print("Saving copy of email for testing and debugging purposes")
        fout.write(msg_content)
        print("File saved")
