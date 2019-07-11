import os
from pathlib import Path

""" Mock directories """

ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) # This is your Project Root
root_dir = Path(ROOT_DIR)

mock_dirs = {
    "email_template": root_dir / "static/email_template",
    "email_final": root_dir / "test/output/email_final"
}

mock_paths = {
    "email_final": mock_dirs["email_final"] / "email.html",
}


mock_names = {
    "name": "johnson",
    "age": 500
}

mock_subjects = {
    "name": "physics",
    "difficulty": "super easy"
}