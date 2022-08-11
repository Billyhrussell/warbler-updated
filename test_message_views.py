"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app, CURR_USER_KEY

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageBaseViewTestCase(TestCase):
    """ Test message base view """
    def setUp(self):
        """ Create test users, messages """

        User.query.delete()
        Message.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)

        db.session.flush()

        m1 = Message(text="m1-text", user_id=u1.id)
        m2 = Message(text="m2-text", user_id=u2.id)
        db.session.add_all([m1, m2])
        db.session.commit()

        self.u1_id = u1.id
        self.u2_id = u2.id
        self.m1_id = m1.id
        self.m2_id = m2.id

        self.client = app.test_client()

    def tearDown(self):
        """ Clean up any fouled transaction """
        db.session.rollback()

    def test_home_messages(self):
        """Test we can see messages if user is logged in """
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get("/")
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text = True)
            self.assertIn("m1-text", html)

    def test_liked_messages(self):
        """Test we can see messages if user is logged in """
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            user1 = User.query.get_or_404(self.u1_id)
            message = Message.query.get_or_404(self.m2_id)
            user1.likes.append(message)

            resp = c.get(f"/users/{self.u1_id}/likes")
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text = True)
            self.assertIn("m2-text", html)

    def test_user_profile_messages(self):
        """Test we can see messages if user is logged in """
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get(f"/users/{self.u1_id}")
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text = True)
            self.assertIn("m1-text", html)


class MessageAddViewTestCase(MessageBaseViewTestCase):
    """Test for message adding """
    def test_add_message(self):
        """Test for adding message when logged in"""
        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            # Now, that session setting is saved, so we can have
            # the rest of ours test
            resp = c.post("/messages/new", data={"text": "Hello"})

            self.assertEqual(resp.status_code, 302)

            Message.query.filter_by(text="Hello").one()

    def test_add_message_logged_out(self):
        """Test cannot add message if not logged in"""
        with self.client as c:

            resp = c.post("/messages/new", data={"text": "Hello"},
                         follow_redirects = True)

            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text = True)
            self.assertIn("Access unauthorized.", html)


class MessageDeleteViewTestCase(MessageBaseViewTestCase):
    """Test for message deleting"""
    def test_delete_message(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            message = Message.query.get_or_404(self.m1_id)

            resp = c.post(f"/messages/{self.m1_id}/delete",
                            follow_redirects = True)

            html = resp.get_data(as_text = True)
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn(message.text, html)

    def test_delete_message_logged_out(self):
        with self.client as c:

            resp = c.post(f"/messages/{self.m1_id}/delete",
                    follow_redirects = True)

            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text = True)
            self.assertIn("Access unauthorized.", html)

    def test_delete_message_not_by_user(self):
        """Test cannot add message for another user"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post(f"/messages/{self.m2_id}/delete",
                            follow_redirects = True)

            html = resp.get_data(as_text = True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)

    # Test add message not by user, not needed?





