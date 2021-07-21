import boto3
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("--folder")
ap.add_argument("--limit")
args = vars(ap.parse_args())
limit = int(args["limit"])
s3 = boto3.resource('s3')
bucket = s3.Bucket("data.ibeyonde")
objects = bucket.objects.filter(Prefix=args["folder"])
count = 0
for object in objects:
    if(count==limit):
        break
    bucket.download_file(object.key, 'temp/%d.jpg'%count)
    count = count + 1
    