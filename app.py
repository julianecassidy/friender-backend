"""Flask app for Friender app."""

import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from werkzeug.exceptions import BadRequest
import jwt


from models import db, connect_db, User, Photo, Match, Like, Dislike
from tokens import create_token

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


####################################################### User Signup/Login/Logout


@app.post('/signup')
def singup():
    """Handle user signup.

    Take inputted JSON user data and create new user in DB. Return JWT.
    If errors, throw BadRequestError.
    """

    try:
        user = User.signup(
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

    token = create_token(request.json["username"])
    return jsonify(token)











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