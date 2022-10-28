"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from pkgutil import get_data
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessagesNewTestCase(TestCase):
    """Test views for route /messages/new"""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_add_message_post(self):
        """Can use add a message?
        /message/new POST
        User already logged in"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_add_message_get(self):
        """Display new message form
        /messages/new  GET
        User already logged in"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
        
            resp = c.get("/messages/new")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Add my message!", html, msg="New message submit button error")
            self.assertIn("happening?", html, msg="Form Text Area error")


class MessageViewTestCase(TestCase):
    """Test views for route /messages/<int:message_id>"""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()
        u = User.query.filter_by(username="testuser").first()
        self.test_message = Message(
            text="Test message here!",
            user_id=u.id
        )
        db.session.add(self.test_message)
        db.session.commit()
        #import pdb; pdb.set_trace()

    def test_message_show(self):
        """Display single message
        /messages/<int:message_id>"""

        m = Message.query.first() # should be only one message in warbler-test db

        with self.client as c:
            resp = c.get(f"/messages/{m.id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Test message here!", html, msg="Test message not in html response")
            self.assertIn("testuser", html, msg="Test user username not in html response")

    def test_messages_destroy_logged_in(self):
        """Delete a message while logged in
        /messages/<int:message_id>/delete POST"""

        m = Message.query.first()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.post(f"/messages/{m.id}/delete")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 302, msg="Successful message delete should redirect")
            self.assertIn("testuser", html, msg="Should redirect to logged in users's profile page")
            self.assertIn('<a href="/users/profile" class="btn btn-outline-secondary">Edit Profile</a>', html, msg="Should be on users's profile page")
            
            ## Need to query and assert that message is not in database ##
    def test_messages_destroy_not_logged_in(self):
        """Delete a message while NOT logged in
        /messages/<int:message_id>/delete POST"""

        m = Message.query.first()

        with self.client as c:
            resp = c.post(f"/messages/{m.id}/delete")
            html = resp.get_data(as_text=True)

            ## Query and assert that message is still in database ##
