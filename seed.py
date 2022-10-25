"""Seed database with sample data from CSV Files."""

from csv import DictReader
from app import db
from models import User, Message, Follows


db.drop_all()
db.create_all()

with open('generator/users.csv') as users:
    db.session.bulk_insert_mappings(User, DictReader(users))

with open('generator/messages.csv') as messages:
    db.session.bulk_insert_mappings(Message, DictReader(messages))

with open('generator/follows.csv') as follows:
    db.session.bulk_insert_mappings(Follows, DictReader(follows))

derp = User(
    username="DerpyMan",
    email="derpyman@derp.com",
    password="abc123"
)
db.session.add(derp)
db.session.commit()


derp_follow1 = Follows(
    user_being_followed_id=200,
    user_following_id=301
)
derp_follow2 = Follows(
    user_being_followed_id=201,
    user_following_id=301
)
derp_mess = Message(
    text="Hi I mak mesuge lulz.",
    user_id=301
)
db.session.add_all([derp_follow1, derp_follow2, derp_mess])
db.session.commit()
