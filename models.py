"""SQL Alchemy models for Friender."""

import os
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
import boto3
from botocore.exceptions import ClientError
from botocore.client import Config
import jwt

load_dotenv()

bcrypt = Bcrypt()
db = SQLAlchemy()

DEFAULT_IMAGE_FILE = "default-image.jpg"
DEFAULT_IMAGE_OBJECT = "username-12345"
SECRET_KEY = os.environ['SECRET_KEY']
USER_IMAGE_BUCKET = "frienderuserphotos"

s3_client = boto3.client(
    's3', 
    aws_access_key_id = os.environ['ACCESS_KEY'], 
    aws_secret_access_key = os.environ['AWS_SECRET_KEY'], 
    config=Config(signature_version='s3v4')
    ) 

AWS_S3_REGION_NAME = "us-east-2"
AWS_S3_SIGNATURE_VERSION = "s3v4"


class Photo(db.Model):
    """Photos storage locations for all users' photos."""

    __tablename__ = "photos"

    file_name = db.Column(
        db.String(),
        primary_key=True
    )

    user_id = db.Column(
        db.Text,
        db.ForeignKey('users.username'),
        nullable=False
    )

    ## Relationship User <-> Photos

    @classmethod
    def upload_photo(cls, file_name, bucket=USER_IMAGE_BUCKET):
        """Uploads a file to Friender user photos bucket on S3. 
        Requires file_name and object_name of the image.
        Returns true if image successfully uploaded or false if not."""

        print("UPLOAD_PHOTO")

        try:
            response = s3_client.upload_file(file_name, bucket, file_name)
        except ClientError as e:
            return False
        return True

    @classmethod
    def get_user_images(cls, image_ids, bucket=USER_IMAGE_BUCKET):
        """Generate URL to provide image source for a user's image."""

        print("GET_USER_IMAGE")

        public_urls = []
        image_paths = [f"uploads/{id}" for id in image_ids]

        try:
            for path in image_paths:
                presigned_url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={
                        'Bucket': bucket,
                        'Key': path},
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
        primary_key=True
    )

    user_2 = db.Column(
        db.Text,
        db.ForeignKey('users.username'),
        primary_key=True
    )

    ## Relationship between User <-> User via Match


class Like(db.Model):
    """Requests to match from a liking user to a liked user."""

    __tablename__ = "likes"

    liking_user = db.Column(
        db.Text,
        db.ForeignKey('users.username'),
        primary_key=True
    )

    liked_user = db.Column(
        db.Text,
        db.ForeignKey('users.username'),
        nullable=False
    )

    ## Relationship between User <-> User via Like


class Dislike(db.Model):
    """Requests not to match from a disliking user to a disliked user."""

    __tablename__ = "dislikes"

    disliking_user = db.Column(
        db.Text,
        db.ForeignKey('users.username'),
        primary_key=True
    )

    disliked_user = db.Column(
        db.Text,
        db.ForeignKey('users.username'),
        nullable=False
    )

    ## Relationship between User <-> User via Dislike


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
        db.String(10),
        nullable=False
    )

    search_radius = db.Column(
        db.Integer,
        nullable=False,
        default=10
    )

    photos = db.relationship('Photo', backref="user")

    matches = db.relationship(
        "User",
        secondary="matches",
        primaryjoin=(Match.user_1 == username),
        secondaryjoin=(Match.user_2 == username),
        backref="matched"
    )

    liked_user = db.relationship(
        "User",
        secondary="likes",
        primaryjoin=(Like.liked_user == username),
        secondaryjoin=(Like.liking_user == username),
        backref="liking_user"
    )

    disliked_user = db.relationship(
        "User",
        secondary="dislikes",
        primaryjoin=(Dislike.disliked_user == username),
        secondaryjoin=(Dislike.disliking_user == username),
        backref="disliking_user"
    )

    @classmethod
    def signup(cls, username, password, name, hobbies, interests, postal_code, search_radius):
        """Sign up user. Hashes password and adds user to database."""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            password=hashed_pwd,
            name=name,
            hobbies=hobbies,
            interests=interests,
            postal_code=postal_code,
            search_radius=search_radius
        )

        db.session.add(user)
        return user
    
    @classmethod
    def login(cls, username, password):
        """Log in user. Find user with "username" and "password" and return that
        user.
        
        If there is no matching username or the password is wrong, return false."""

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user
        
        return False

    @classmethod
    def create_token(cls, username):
        """Create a JWT for user and return."""

        return jwt.encode({"username": username}, SECRET_KEY, algorithm="HS256")

    def serialize(self):
        """Make a dictionary of current user instance."""

        user = {
            "username": self.username,
            "name": self.name,
            "interests": self.interests,
            "hobbies": self.hobbies,
            "postal_code": self.postal_code,
            "search_radius": self.search_radius}
        
        return user

def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    app.app_context().push()
    db.app = app
    db.init_app(app)
