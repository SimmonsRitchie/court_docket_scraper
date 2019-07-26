"""
This module moves files to an s3 bucket from an ec2 instance
"""
# inbuilt or third party libs
import boto3
import logging
import os

# project modules
from locations import paths
from modules.email import email_error_notification

def copy_file_to_s3_bucket():

    try:
        # GET ENV VARS
        bucket_name = os.environ.get("BUCKET_NAME")
        keyID = os.environ.get("KEY_ID")
        sKeyID = os.environ.get("SECRET_KEY_ID")
        source_path = str(paths["payload_json"].resolve())
        destination_path = os.environ.get("DESTINATION_PATH")

        # LOGGING
        logging.info(f"Moving {source_path} to S3 bucket {bucket_name}...")
        logging.info(f"File will be saved in: {destination_path}")

        # CONNECT TO S3
        session = boto3.Session(
            aws_access_key_id=keyID,
            aws_secret_access_key=sKeyID,
        )
        s3 = session.resource('s3')

        # UPLOAD
        s3.Bucket(bucket_name).upload_file(source_path, destination_path)
        logging.info(f"file uploaded to {destination_path}")
    except Exception as e:
        error_summary = "Something went wrong when attempting to copy file" \
                        " to S3 bucket"
        logging.exception(e)
        email_error_notification(error_summary, e)
        return

