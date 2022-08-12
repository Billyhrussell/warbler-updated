""" User views tests """

import os
from unittest import TestCase

from models import db, User, Message, Follows

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


class UserBaseViewTestCase(TestCase):
    """ Test message base view """
    def setUp(self):
        """ Create test users, messages """

        User.query.delete()
        Message.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)
        u3 = User.signup("u3", "u3@email.com", "password", None)

        db.session.flush()

        self.u1_id = u1.id
        self.u2_id = u2.id
        self.u3_id = u3.id

        u1.followers.append(u2)
        u2.followers.append(u1)

        db.session.add_all([u1,u2])
        db.session.commit()
        self.client = app.test_client()

    def tearDown(self):
        """ Clean up any fouled transaction """
        db.session.rollback()

    def test_following_page(self):
        """Test that a user can see who they are following"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get(f"/users/{self.u1_id}/following")

            following = User.query.get_or_404(self.u2_id)

            html = resp.get_data(as_text = True)
            self.assertIn(following.username, html)
            self.assertEqual(resp.status_code, 200)

    def test_followers_page(self):
        """Test that a user can see their followers"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get(f"/users/{self.u1_id}/followers")

            followers = User.query.get_or_404(self.u2_id)

            html = resp.get_data(as_text = True)
            self.assertIn(followers.username, html)
            self.assertEqual(resp.status_code, 200)

    def test_unfollow_user(self):
        """Test that a user can unfollow another user"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post(f"/users/stop-following/{self.u2_id}",
                            follow_redirects = True)

            following = User.query.get_or_404(self.u2_id)

            html = resp.get_data(as_text = True)
            self.assertNotIn(following.username, html)
            self.assertEqual(resp.status_code, 200)

    def test_follow_user(self):
        """Test that a user can follow another user"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post(f"/users/follow/{self.u3_id}",
                            follow_redirects = True)


            u3 = User.query.get_or_404(self.u3_id)

            html = resp.get_data(as_text = True)
            self.assertIn(u3.username, html)
            self.assertEqual(resp.status_code, 200)

            #todo: add values we know

            # with self.client as c:
            # with c.session_transaction() as sess:
            #     sess[CURR_USER_KEY] = self.u1_id

            # u3 = User.signup("u3", "u3@email.com", "password", None)

            # resp = c.post(f"/users/follow/{u3.id}",
            #                 follow_redirects = True)

            # u3 = User.query.filter_by(username = "u3")

            # html = resp.get_data(as_text = True)
            # self.assertIn(u3.username, html)
            # self.assertEqual(resp.status_code, 200)


    def test_following_logged_out(self):
        """Test that a user cannot see followers if logged out"""
        with self.client as c:
            resp = c.get(f"/users/{self.u1_id}/following",
                            follow_redirects=True)

            html = resp.get_data(as_text = True)
            self.assertIn("Access unauthorized.", html)
            self.assertEqual(resp.status_code, 200)

    def test_followers_logged_out(self):
        """Test that a user cannot see following if logged out"""
        with self.client as c:
            resp = c.get(f"/users/{self.u1_id}/followers",
                            follow_redirects=True)

            html = resp.get_data(as_text = True)
            self.assertIn("Access unauthorized.", html)
            self.assertEqual(resp.status_code, 200)
