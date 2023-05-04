import os
import jwt

SECRET_KEY = os.environ['SECRET_KEY']


def create_token(username):
    """Create a JWT for user and return."""

    return jwt.encode({"payload": username}, SECRET_KEY)