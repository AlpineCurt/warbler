"""User View tests"""

import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

db.drop_all()
db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class UserViewsTestCase(TestCase):
    """Test views for route /users"""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser1 = User.signup(username="testuser_one",
                                    email="test@test.com",
                                    password="testuser1",
                                    image_url=None)
        
        self.testuser2 = User.signup(username="testuser_two",
                                    email="testtwo@test.com",
                                    password="testuser2",
                                    image_url=None)
        
        self.testuser3 = User.signup(username="testuser_three",
                                    email="testthree@test.com",
                                    password="testuser3",
                                    image_url=None)

        db.session.commit()

        # testuser_one is following testuser_two
        f1 = Follows(
            user_being_followed_id=self.testuser2.id,
            user_following_id=self.testuser1.id
        )
        # testuser_three is following testuser_one
        f2 = Follows(
            user_being_followed_id=self.testuser1.id,
            user_following_id=self.testuser3.id
        )
        db.session.add_all([f1, f2])
        db.session.commit()
    
    def test_users_show(self):
        """Display list of users
        /users GET"""

        with self.client as c:
            resp = c.get("/users")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser_one", html, msg="The test user username should be in html")

    def test_users_show(self):
        """Display single user profile
        /users/<int:user_id> GET"""

        m = Message(
            text="Hello, I am test message",
            user_id=self.testuser1.id
        )
        db.session.add(m)
        db.session.commit()

        with self.client as c:
            resp = c.get(f"/users/{self.testuser1.id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser_one", html, msg="username should be in html")
            self.assertIn("Hello, I am test message", html, msg="Test message should get queried and displayed")

    def test_show_following_not_logged_in(self):
        """Show list of people user_id is following while NOT logged in
        /users/<int:user_id/following GET>"""
        
        with self.client as c:
            resp = c.get(f"/users/{self.testuser1.id}/following")

            self.assertEqual(resp.status_code, 302)
    
    def test_show_following_logged_in(self):
        """Show list of people user_id is following while logged in
        /users/<int:user_id/following GET>"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id
            
            resp = c.get(f"/users/{self.testuser1.id}/following")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser_two", html, msg="testuser2 should appear in list")
            self.assertNotIn("testuser_three", html, msg="testuser3 is not followed by testuser1; should not appear")

    def test_users_followers_not_logged_in(self):
        """Show list of followers while NOT logged in
        /users/<int:user_id>/followers GET"""

        with self.client as c:
            resp = c.get(f"/users/{self.testuser1.id}/followers")
            self.assertEqual(resp.status_code, 302)
    
    def test_users_followers_logged_in(self):
        """Show list of followers while logged in
        /users/<int:user_id>/followers GET"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id
            
            resp = c.get(f"/users/{self.testuser1.id}/followers")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser_three", html, msg="following user did not show")
            self.assertNotIn("testuser_two", html, msg="a non-following user appeared")
    
    def test_add_follow_not_logged_in(self):
        """Add follow while NOT logged in
        /users/follow/<int:follow_id> POST"""

        with self.client as c:
            resp = c.post(f"/users/follow/{self.testuser2.id}")
            self.assertEqual(resp.status_code, 302)

            follow_list = Follows.query.all()
            self.assertEqual(len(follow_list), 2, msg="No new follows should be added")
    
    # def test_add_follow_logged_in(self):
    #     """Add follow while logged in
    #     /users/follow/<int:follow_id> POST"""

    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.testuser1.id
            
    #         # testuser1 is trying to follow testuser3
    #         resp = c.post(f"/users/follow/{self.testuser3.id}")
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn("testuser_two", html, msg="existing followed user did not show")
    #         self.assertIn("testuser_three", html, msg="added followed user did not show")

    #         follow_list = Follows.query.all()
    #         self.assertEqual(len(follow_list), 3, msg="new Follow should be added to db")
    
    def test_user_profile_not_logged_in(self):
        """/users/profile GET"""

        with self.client as c:
            resp = c.get("/users/profile")
            self.assertEqual(resp.status_code, 302)
    
    def test_user_profile_logged_in(self):
        """Edit user profile
        /users/profile GET"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id
            
            resp = c.get("/users/profile")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser_one", html)
            self.assertIn("Edit Your Profile", html)
    
    def test_user_profile_edit_not_logged_in(self):
        """Edit user profile NOT logged in
        /users/profile POST"""

        with self.client as c:
            resp = c.post("/users/profile")
            self.assertEqual(resp.status_code, 302)
    
    def test_user_profile_edit_logged_in(self):
        """Edit user profile while logged in
        /users/profile POST"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id
            
            resp = c.post(
                "/users/profile",
                data={
                    "username": "testuser_one",
                    "password": "testuser1",
                    "email": "newemail@newmail.com",
                    "image_url": "www.whatever.com",
                    "header_image_url": "www.idontcare.com",
                    "bio": "I am test user."
                    }
                )
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 302)

            user1 = User.query.filter_by(username="testuser_one").first()
            self.assertEqual("newemail@newmail.com", user1.email, msg="email not updated")
            self.assertEqual("I am test user.", user1.bio, msg="bio not updated")
    
    def test_delete_user_not_logged_in(self):
        """Delete user while NOT logged in
        /users/delete POST"""

        with self.client as c:
            resp = c.post("/users/delete")
            self.assertEqual(resp.status_code, 302)

            users = User.query.all()
            self.assertEqual(len(users), 3, msg="A user got deleted that should not have")
    
    def test_delete_user_logged_in(self):
        """Delete user while logged in
        /users/delete POST"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id
        
        resp = c.post("/users/delete")
        html = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/signup", html)
        users = User.query.all()
        self.assertEqual(len(users), 2, msg="User did not get deleted")