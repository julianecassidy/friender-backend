"""Flask app for Friender app."""

import os
from flask import Flask, redirect, render_template, request
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.utils import secure_filename

from models import db, connect_db, Photos
from s3 import upload_photo, get_user_image
# from forms import #FORMS HERE

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

@app.route("/")
def home():
    """Render temporary homepage with image submission form and viewable images."""
    images = get_user_image()
    print("IMAGES", images)
    return render_template('base.html', images=images)


@app.route("/upload", methods=["POST"])
def upload():
    """Upload image file from form to AWS S3."""

    if request.method == "POST":
        f = request.files['image-file']
        f.save(os.path.join(UPLOAD_FOLDER, secure_filename(f.filename)))
        print("FILENAME IN APP", f"uploads/{f.filename}")
        upload_photo(f"uploads/{f.filename}")
        return redirect("/")