"""SQL Alchemy models for Friender."""

import os
from datetime import datetime
# from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
import boto3
from botocore.exceptions import ClientError


# bcrypt = Bcrypt()
db = SQLAlchemy()

DEFAULT_IMAGE_FILE = "default-image.jpg"
DEFAULT_IMAGE_OBJECT = "username-12345"

s3_client = boto3.client('s3') 
                                 ##aws_access_key_id = ACCESS_KEY, aws_secret_access_key = AWS_SECRET_KEY)

# class User(db.Model):

class Photos(db.Model):
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


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    app.app_context().push()
    db.app = app
    db.init_app(app)