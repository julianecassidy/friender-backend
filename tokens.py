import os
import jwt
from flask import jsonify

SECRET_KEY = os.environ['SECRET_KEY']


def create_token(username):
    """Create a JWT for user and return."""

    payload = {username}
    return jwt.encode(jsonify(payload), SECRET_KEY)