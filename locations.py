"""
This program uses an number of paths and directories to store information that needs to be written and read. This
file is a repository for those locations.
"""

from pathlib import Path
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) # This is your Project Root
root_dir = Path(ROOT_DIR)


# DIRECTORIES
test_dirs = {
    "pdfs": root_dir / "temp/pdfs",
    "extracted_text": Path("temp/extracted_text"),
    "payload_email": Path("temp/payload_email"),
    "payload_csv": Path("temp/payload_csv"),
    "payload_json": Path("temp/payload_json"),
    "email_final": root_dir / "temp/email_final",
    "email_template": root_dir / "static/email_template"
}

# PATHS
# Temp files that we will need to read and write to multiple times throughout program run.
test_paths = {
    "payload_email": test_dirs["payload_email"] / "email.html",
    "payload_csv": test_dirs["payload_csv"] / "dockets.csv",
    "payload_json": test_dirs["payload_json"] / "dockets.json",
    "email_final": test_dirs["email_final"] / "email.html",
}

# TESTING LOCATIONS
"""
We use a different set of directories and paths for testing input and output. We mock this dictionary in our tests.
"""

mock_dirs = {
    "email_template": root_dir / "static/email_template",
    "email_final": root_dir / "test/output/email_final"
}

mock_paths = {
    "email_final": mock_dirs["email_final"] / "email.html",
}
