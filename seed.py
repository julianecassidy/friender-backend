"""Seed file for Friender app."""

from app import app
from models import db, User, Photo, Match, Like, Dislike

db.drop_all()
db.create_all()

u1 = User(
    username="indy",
    password="password",
    name="Indy",
    hobbies="chasing squirrels",
    interests="food and walks",
    postal_code=80113,
    search_radius=20
)

u2 = User(
    username="petey",
    password="password",
    name="Peter",
    hobbies="napping",
    interests="his person",
    postal_code=80204
)

u3 = User(
    username="griff",
    password="password",
    name="Griff",
    hobbies="barking incessantly",
    interests="waiting for the mailman",
    postal_code=95762,
    search_radius=20
)

u4 = User(
    username="dottie",
    password="password",
    name="Dottie Lou",
    hobbies="destroying things",
    interests="everything",
    postal_code=80110,
    search_radius=5
)

db.session.add_all([u1, u2, u3, u4])
db.session.commit()