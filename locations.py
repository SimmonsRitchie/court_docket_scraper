"""
This program uses an number of paths and directories to store information that needs to be written and read. This
file is a repository for those locations.
"""

from pathlib import Path
import os

# This sets our root directory as the project directory
ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) # This is your Project Root
root_dir = Path(ROOT_DIR)

temp_dir = root_dir / "temp/"
static_dir= root_dir / "static/"

# DIRECTORIES
dirs = {
    "pdfs": temp_dir / "pdfs",
    "extracted_text": temp_dir / "extracted_text",
    "payload_email": temp_dir / "payload_email",
    "payload_csv": temp_dir / "payload_csv",
    "payload_json": temp_dir / "payload_json",
    "email_final": temp_dir / "email_final",
    "email_template": static_dir / "email_template",
    "logs": root_dir / "logs"
}

# PATHS
# Many of our filenames are generated dynamically during runtime (eg. downloaded PDFs are in format {docketnum}.pdf,
# however the following are files with static filenames:
paths = {
    "payload_email": dirs["payload_email"] / "email.html",
    "payload_csv": dirs["payload_csv"] / "dockets.csv",
    "payload_json": dirs["payload_json"] / "dockets.json",
    "email_final": dirs["email_final"] / "email.html",
    "logs_config": dirs["logs"] / "config/logging.yaml"
}
