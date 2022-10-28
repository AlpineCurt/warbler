"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
    
    def test_signup(self):
        """User.signup method"""

        email1="user1@test.com",
        username1="test1",
        password1="itsasecret"

        user1 = User.signup(
            email=email1,
            username=username1,
            password=password1,
            image_url=User.image_url.default.arg
        )

        self.assertIsInstance(user1, User)

        user1_query = User.query.filter_by(username="test1").first()
        self.assertNotEqual(
            user1_query.password,
            'itsasecret',
            msg="Password should be hashed")
    
    def test_authenticate(self):
        """User.authenticate method"""

        email1="user1@test.com",
        username1="test1",
        password1="itsasecret"

        user1 = User.signup(
            email=email1,
            username=username1,
            password=password1,
            image_url=User.image_url.default.arg
        )

        user1_auth = User.authenticate("test1", "itsasecret")
        self.assertIsInstance(
            user1_auth,
            User,
            msg="Valid password should return User object")
        
        user1_bad_password = User.authenticate("test1", "wrongpassword")
        self.assertFalse(user1_bad_password, msg="Wrong password should return False")

        user1_bad_username = User.authenticate("test2", "itsasecret")
        self.assertFalse(user1_bad_username, msg="Wrong username should return False")
