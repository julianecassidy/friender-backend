import os
from flask import request, g
from functools import wraps
from werkzeug.exceptions import BadRequest, Unauthorized
from models import User
import jwt

def require_user(f):
    """Check request has a valid JWT for logged in user."""

    @wraps(f)
    def decorated(*args, **kwargs):
        if g.user:
            return f(*args, **kwargs)
        
        else:
            raise Unauthorized()
    
    return decorated