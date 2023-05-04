"""Flask app for Friender app."""

import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from werkzeug.exceptions import BadRequest, Unauthorized
import jwt


from models import db, connect_db, User, Photo, Match, Like, Dislike
from auth_middleware import require_user

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
UPLOAD_FOLDER = "uploads"

connect_db(app)

# Having the Debug Toolbar show redirects explicitly is often useful;
# however, if you want to turn it off, you can uncomment this line:
#
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)


################################################################################
#  User Signup/Login/Logout

@app.before_request
def add_user_to_g():
    """If there is a user logged in, add the current user to Flask global."""

    token = None
    if "Authorization" in request.headers:
        token = request.headers["Authorization"]

    if token:
        try:
            data = jwt.decode(token, os.environ['SECRET_KEY'], algorithms=["HS256"])
            print("IS THERE ERROR HERE?")
            current_user = User.query.get(data["username"])
            if current_user is None:
                raise Unauthorized("Invalid token.")
            else:
                g.user = current_user
            
        except Exception as e:
            raise Unauthorized("Invalid token")
    
    else:
        g.user = None
    
    

@app.post('/signup')
def signup():
    """Handle user signup.

    Take inputted JSON user data and create new user in DB. Return JWT.
    If errors, throw BadRequest Error.
    """

    try:
        User.signup(
            username=request.json["username"],
            password=request.json["password"],
            name=request.json["name"],
            hobbies=request.json["hobbies"],
            interests=request.json["interests"],
            postal_code=request.json["postal_code"],
            search_radius=request.json["search_radius"],
        )
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        raise BadRequest("Username already in use. No user created.")

    token = User.create_token(request.json["username"])
    return jsonify(token)


@app.post('/login')
def login():
    """Handle user login.

    Taken JSON username and password. Return JWT if valid user.
    If invalid, throw Unauthorized Error."""

    user = User.login(
        username=request.json["username"],
        password=request.json["password"]
    )

    if user:
        token = User.create_token(user.username)
        return jsonify(token)
    
    else:
        raise Unauthorized("Username/password invalid.")


################################################################################
# User Routes

@app.get('/users/<username>')
@require_user
def get_user(username):
    """Get user from database. Must be logged in."""

    user_instance = User.query.get_or_404(username)
    user = user_instance.serialize()
    return jsonify(user)

@app.patch('/users/<username>')
@require_user
def update_user_profile(username):
    """Update a user's information. Must be logged in as same user in params."""

    if username != g.user.username:
        raise Unauthorized
    
    user = User.query.get_or_404(username)

    user.name = request.json["name"]
    user.hobbies=request.json["hobbies"],
    user.interests=request.json["interests"],
    user.postal_code=request.json["postal_code"],
    user.search_radius=request.json["search_radius"]

    db.session.commit()

    updated_user_instance = User.query.get(username)
    updated_user = updated_user_instance.serialize()
    return jsonify(updated_user)
    
@app.delete('/users/<username>')
@require_user
def delete_user(username):
    """Delete a user's account. Must be logged in as same user in params."""

    if username != g.user.username:
        raise Unauthorized
    
    Match.query.filter(or_(
        Match.user_1==username, 
        Match.user_2==username
    )).delete()

    Like.query.filter(or_(
        Like.liking_user==username, 
        Like.liked_user==username
    )).delete()
    
    Dislike.query.filter(or_(
        Dislike.disliking_user==username, 
        Dislike.disliked_user==username
    )).delete()
    
    Photo.query.filter(Photo.user_id==username).delete()
    db.session.delete(g.user)
    db.session.commit()

    return f"{username} deleted"




# @app.route("/")
# def home():
#     """Render temporary homepage with image submission form and viewable images."""
#     images = get_user_image()
#     print("IMAGES", images)
#     return render_template('base.html', images=images)


# @app.route("/upload", methods=["POST"])
# def upload():
#     """Upload image file from form to AWS S3."""

#     if request.method == "POST":
#         f = request.files['image-file']
#         f.save(os.path.join(UPLOAD_FOLDER, secure_filename(f.filename)))
#         print("FILENAME IN APP", f"uploads/{f.filename}")
#         upload_photo(f"uploads/{f.filename}")
#         return redirect("/")
