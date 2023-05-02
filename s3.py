import os
import boto3
from botocore.exceptions import ClientError
from botocore.client import Config

s3_client = boto3.client(
    's3', 
    aws_access_key_id = os.environ['ACCESS_KEY'], 
    aws_secret_access_key = os.environ['AWS_SECRET_KEY'], 
    config=Config(signature_version='s3v4')
    ) 

AWS_S3_REGION_NAME = "us-east-2"

AWS_S3_SIGNATURE_VERSION = "s3v4"

	
# s3 = boto3.resource(
#     's3',
#     aws_access_key_id='xxxxxx',
#     aws_secret_access_key='xxxxxx',
    
# )

def upload_photo(file_name, bucket="frienderuserphotos"):
    """Uploads a file to Friender user photos bucket on S3. 
    Requires file_name and object_name of the image.
    Returns true if image successfully uploaded or false if not."""

    try:
        response = s3_client.upload_file(file_name, bucket, file_name)
    except ClientError as e:
        print(e)
        return False
    return True


def get_user_image(bucket="frienderuserphotos"):
    """Generate URL to provide image source for a user's image."""

    print("GET_USER_IMAGE")

    public_urls = []
    user_photos = ['uploads/rv.jpg', 'uploads/tree.jpg', 'uploads/MetLife.png']

    try:
        for item in user_photos:
            presigned_url = s3_client.generate_presigned_url('get_object', Params = {'Bucket': bucket, 'Key': item}, ExpiresIn = 3600)
            public_urls.append(presigned_url)
    except Exception as e:
        pass
    # print("[INFO] : The contents inside show_image = ", public_urls)
    return public_urls