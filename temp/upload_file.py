import boto3
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("--key")
ap.add_argument("--file")
args = vars(ap.parse_args())
s3 = boto3.resource('s3')
bucket = s3.Bucket("data.ibeyonde")

bucket.upload_file(args['file'], args['key'])