"""SQL Alchemy models for Friender."""

import os
from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
import boto3
from botocore.exceptions import ClientError


bcrypt = Bcrypt()
db = SQLAlchemy()

DEFAULT_IMAGE_FILE = "default-image.jpg"
DEFAULT_IMAGE_OBJECT = "username-12345"

s3_client = boto3.client('s3') 
                                 ##aws_access_key_id = ACCESS_KEY, aws_secret_access_key = AWS_SECRET_KEY)

# class User(db.Model):

class Photos(db.Model):
    """Photos storage locations for all users' photos."""

    __tablename__ = "photos"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    file_name = db.Column(
        db.Text,
        nullable=False
    )

    object_name = db.Column(
        db.Text,
        nullable=False
    )

    user_id = db.Column(
        db.Text,
        db.ForeignKey('users.username'),
        nullable=False
    ) 


    @classmethod
    def upload_photo(file_name, object_name, bucket="friender_user_photos"):
        """Uploads a file to Friender user photos bucket on S3. 
        Requires file_name and object_name of the image.
        Returns true if image successfully uploaded or false if not."""

        try:
            response = s3_client.upload_file(file_name, bucket, object_name)
        except ClientError as e:
            print(e)
            return False
        return True


    @classmethod
    def get_user_photos(object_name, bucket="friender_user_photos", expiration=3600):
        """Generate URL to provide image source for a user's image."""

        try:
            response = s3_client.generate_presigned_url('get_object',
                                                        Params={'Bucket': bucket,
                                                                'Key': object_name},
                                                        ExpiresIn=expiration)
        except ClientError as e:
            print(e)
            return None
        
        return response



def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    app.app_context().push()
    db.app = app
    db.init_app(app)