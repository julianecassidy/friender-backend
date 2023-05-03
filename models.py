"""SQL Alchemy models for Friender."""

import os
from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
import boto3
from botocore.exceptions import ClientError
from botocore.client import Config


bcrypt = Bcrypt()
db = SQLAlchemy()

DEFAULT_IMAGE_FILE = "default-image.jpg"
DEFAULT_IMAGE_OBJECT = "username-12345"

s3_client = boto3.client(
    's3', 
    aws_access_key_id = os.environ['ACCESS_KEY'], 
    aws_secret_access_key = os.environ['AWS_SECRET_KEY'], 
    config=Config(signature_version='s3v4')
    ) 

AWS_S3_REGION_NAME = "us-east-2"
AWS_S3_SIGNATURE_VERSION = "s3v4"


class User(db.Model):
    """App user login and profile info."""

    __tablename__ = "users"

    username = db.Column(
        db.Text,
        primary_key=True
    )

    password = db.Column(
        db.Text,
        nullable=False
    )

    name = db.Column(
        db.String(30),
        nullable=False
    )

    hobbies = db.Column(
        db.Text,
        nullable=False,
        default=''
    )

    interests = db.Column(
        db.Text,
        nullable=False,
        default=''
    )

    postal_code = db.Column(
        db.Integer,
        nullable=False
    )

    search_radius = db.Column(
        db.Integer,
        nullable=False,
        default=10
    )


class Photo(db.Model):
    """Photos storage locations for all users' photos."""

    __tablename__ = "photos"

    file_name = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Text,
        db.ForeignKey('users.username'),
        nullable=False
    )

    @classmethod
    def upload_photo(self, file_name, bucket="friender_user_photos"):
        """Uploads a file to Friender user photos bucket on S3. 
        Requires file_name and object_name of the image.
        Returns true if image successfully uploaded or false if not."""

        print("FILENAME IN MODELS", file_name)
        try:
            response = s3_client.upload_file(file_name, bucket, file_name)
        except ClientError as e:
            print(e)
            return False
        return True

    @classmethod
    def get_user_image(bucket="frienderuserphotos"):
        """Generate URL to provide image source for a user's image."""

        print("GET_USER_IMAGE")

        public_urls = []
        user_photos = ['uploads/rv.jpg',
                       'uploads/tree.jpg', 'uploads/MetLife.png']

        try:
            for item in user_photos:
                presigned_url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={
                        'Bucket': bucket,
                        'Key': item},
                    ExpiresIn=3600)
                public_urls.append(presigned_url)
        except Exception as e:
            pass
        # print("[INFO] : The contents inside show_image = ", public_urls)
        return public_urls
    

class Match(db.Model):
    """Matches where both users have requested the other."""

    __tablename__ = "matches"

    user_1 = db.Column(
        db.Text,
        db.ForeignKey('users.username'),
        nullable=False
    )

    user_2 = db.Column(
        db.Text,
        db.ForeignKey('users.username'),
        nullable=False
    )


class Request(db.Model):
    """Requests to match from a liking user to a liked user."""

    __tablename__ = "requests"

    liking_user = db.Column(
        db.Text,
        db.ForeignKey('users.username'),
        nullable=False
    )

    liked_user = db.Column(
        db.Text,
        db.ForeignKey('users.username'),
        nullable=False
    )


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    app.app_context().push()
    db.app = app
    db.init_app(app)
