import boto3
import logging
import os




def check_file_exists_in_s3_bucket(bucket_name, dst_path):

    # Get bucket access keys
    keyID = os.environ.get("KEY_ID")
    sKeyID = os.environ.get("SECRET_KEY_ID")

    # connect
    logging.info(f"Checking whether {dst_path} exists in {bucket_name}")
    session = boto3.Session(
        aws_access_key_id=keyID,
        aws_secret_access_key=sKeyID,
    )
    s3 = session.resource('s3')

    # check file exists
    bucket = s3.Bucket(bucket_name)
    objs = list(bucket.objects.filter(Prefix=dst_path))
    if len(objs) > 0 and objs[0].key == dst_path:
        logging.info("Exists!")
        return True
    else:
        logging.info("Doesn't exist")
        return False

def delete_key_in_bucket(bucket_name, dst_path):

    # Get bucket access keys
    keyID = os.environ.get("KEY_ID")
    sKeyID = os.environ.get("SECRET_KEY_ID")

    # connect
    logging.info(f"Deleting {dst_path} from {bucket_name}")
    session = boto3.Session(
        aws_access_key_id=keyID,
        aws_secret_access_key=sKeyID,
    )
    s3 = session.resource('s3')
    bucket = s3.Bucket(bucket_name)
    try:
        bucket.objects.filter(Prefix=dst_path).delete()
    except Exception as e:
        logging.error(f"Something went wrong when attempting to delete "
                      f"{dst_path}")
        logging.exception(e)
        raise