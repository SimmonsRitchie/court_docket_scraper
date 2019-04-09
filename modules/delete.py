"""
This modules deletes list of directories created during the last scrape
(if there was a previous scrape) and deletes them so that we won't have a confusing
array of files when we re-run the program.
"""

import os
from shutil import rmtree


def delete_temp_files(list_of_folders_to_delete):
    print("Checking that temp files have been deleted from previous scraper runs")
    for folder in list_of_folders_to_delete:

        path_of_folder = os.path.abspath(folder)
        if os.path.exists(path_of_folder):
            print("Deleting {}...".format(folder))
            try:
                rmtree(path_of_folder)
                print("Successfully deleted the directory and all files inside")
            except OSError:
                print("Deletion of the directory %s failed for some reason" % path_of_folder)
        else:
            print("No folder named {} detected".format(folder))
