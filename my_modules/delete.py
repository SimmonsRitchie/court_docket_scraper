import os
from shutil import rmtree

def delete_temp_files(base_folder_pdfs,base_folder_email,base_folder_text):
    print("Checking that temp files have been deleted from previous scraper runs")
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