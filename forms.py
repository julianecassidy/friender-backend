"""Forms for Friender app."""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length, Optional, NumberRange


class SignupForm(FlaskForm):
    """Form for adding a new user."""

    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=3, max=30)]
    )

    password = PasswordField(
        'Password',
        validators=[Length(min=6)]
    )

    name = StringField(
        'First Name',
        validators=[DataRequired(), Length(max=30)]
    )

    hobbies = TextAreaField(
        'Hobbies',
        validators=[Optional()]
    )

    interests = TextAreaField(
        'Interests',
        validators=[Optional()]
    )

    postal_code = IntegerField(
        'Zip Code',
        validators=[DataRequired(), NumberRange(min=10000)]
    )

    search_radius = IntegerField(
        'Maxium distance in miles (this won\'t be shown to other users)',
        validators=[DataRequired(), NumberRange(min=5, max=200)]
    )