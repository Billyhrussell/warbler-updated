"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """ Tests models for User """
    def setUp(self):
        """ Create test users """
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)

        db.session.commit()
        self.u1_id = u1.id
        self.u2_id = u2.id

        self.client = app.test_client()

    def tearDown(self):
        """ Clean up any fouled transaction """
        db.session.rollback()

    def test_user_model(self):
        """ Test that users don't have any messages or followers to start """
        u1 = User.query.get(self.u1_id)

        # User should have no messages & no followers
        self.assertEqual(len(u1.messages), 0)
        self.assertEqual(len(u1.followers), 0)

    def test_repr(self):
        """ Test that the user repr works """
        user = User.query.get_or_404(self.u1_id)

        self.assertEqual(f"{user}", f"<User #{user.id}: {user.username}, {user.email}>")

    def test_is_following(self):
        """ Test for following relationship """
        user1 = User.query.get_or_404(self.u1_id)
        user2 = User.query.get_or_404(self.u2_id)

        user1.following.append(user2)

        self.assertIn(user2, user1.following)
        self.assertTrue(user1.following)

        user1.following.remove(user2)

        self.assertEqual(user1.following, [])

    def test_is_followed_by(self):
        """ Test for followed relationship """
        user1 = User.query.get_or_404(self.u1_id)
        user2 = User.query.get_or_404(self.u2_id)

        user2.following.append(user1)

        self.assertIn(user2, user1.followers)

        user1.followers.remove(user2)

        self.assertEqual(user1.followers, [])

    def test_user_signup(self):
        """ Test User signup """

        user3 = User.signup("u3", "u3@email.com", "password")

        all_users = User.query.all()

        self.assertIn(user3, all_users)

        try:
            bad_user = User.signup("u3", "bad_user@email.com", "password")

        except:
            all_users = User.query.all()
            self.assertNotIn(bad_user, all_users)  # not going into except?

    def test_user_authenticate(self):
        """ Test authentication of a user """
        user1 = User.query.get_or_404(self.u1_id)

        user = User.authenticate(user1.username, 'password') # can't user user1.password because it's already hashed
        self.assertEqual(user, user1)

        bad_user = User.authenticate('wrong username', 'password')
        self.assertFalse(bad_user)

        bad_user = User.authenticate(user1.username, 'wrong password')
        self.assertFalse(bad_user)