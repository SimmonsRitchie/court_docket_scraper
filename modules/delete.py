import os
from shutil import rmtree

def delete_temp_files(base_folder_pdfs,base_folder_email,base_folder_json,base_folder_csv,base_folder_text):
    print("Checking that temp files have been deleted from previous scraper runs")

    # DELETE PDF FOLDER
    path = os.path.abspath(base_folder_pdfs)
    if os.path.exists(path):
        print("Deleting PDF folder and contents...")
        try:
            rmtree(path)
            print("Successfully deleted the directory %s and all files inside" % base_folder_pdfs)
        except OSError:
            print("Deletion of the directory %s failed for some reason" % path)
    else:
        print("No PDF folder detected")

    # DELETE EMAIL PAYLOAD FOLDER
    path = os.path.abspath(base_folder_email)
    if os.path.exists(path):
        print("Deleting email payload folder...")
        try:
            rmtree(path)
            print("Successfully deleted the directory %s and all files inside" % base_folder_email)
        except OSError:
            print("Deletion of the directory %s failed for some reason" % path)
    else:
        print("No email payload folder detected")

    # DELETE JSON PAYLOAD FOLDER
    path = os.path.abspath(base_folder_json)
    if os.path.exists(path):
        print("Deleting JSON payload folder...")
        try:
            rmtree(path)
            print("Successfully deleted the directory %s and all files inside" % base_folder_email)
        except OSError:
            print("Deletion of the directory %s failed for some reason" % path)
    else:
        print("No JSON payload folder detected")

    # DELETE CSV PAYLOAD FOLDER
    path = os.path.abspath(base_folder_csv)
    if os.path.exists(path):
        print("Deleting CSV payload folder...")
        try:
            rmtree(path)
            print("Successfully deleted the directory %s and all files inside" % base_folder_email)
        except OSError:
            print("Deletion of the directory %s failed for some reason" % path)
    else:
        print("No CSV payload folder detected")

    # DELETE CONVERTED PDF TEXT FILES
    path = os.path.abspath(base_folder_text)
    if os.path.exists(path):
        print("Deleting extracted text folder...")
        try:
            rmtree(path)
            print("Successfully deleted the directory %s and all files inside" % base_folder_text)
        except OSError:
            print("Deletion of the directory %s failed for some reason" % path)
    else:
        print("No extracted text folder detected")