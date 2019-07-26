"""
This module moves files to an s3 bucket from an ec2 instance
"""
import boto
from boto.s3.key import Key
import time
import logging

def move_file_to_s3_bucket():

    file_name = "bokchoy.txt"
    bucket_name = "penn-playground"
    file = open(file_name)

    conn = boto.connect_s3()
    bucket = conn.get_bucket(bucket_name)

    print("Moving file...")
    #Get the Key object of the bucket
    k = Key(bucket)
    #Crete a new key with id as the name of the file
    k.key=file_name
    #Upload the file
    result = k.set_contents_from_file(file)
    #result contains the size of the file uploaded
    print("file moved")