"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


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

class MessageModelTestCase(TestCase):
    """Test Class for Message Model"""

    def setUp(self):
        """Create test client, add sample data"""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        test_user = User.signup(
            email="user1@test.com",
            username="test1",
            password="itsasecret",
            image_url=User.image_url.default.arg
        )
        db.session.commit()

    def test_message_model(self):
        """Does the basic model work?"""

        test_user = User.query.filter_by(username="test1").first()

        m = Message(
            text="Hi, I am post!",
            user_id=test_user.id
        )

        db.session.add(m)
        db.session.commit()

        self.assertNotEqual(m.timestamp, '', msg="timestamp not set correctly")
        self.assertEqual(m.user.username, "test1", msg="message username incorrect.")
        self.assertEqual(len(m.likes), 0)