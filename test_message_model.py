""" Message model tests """

import os
from unittest import TestCase

from models import db, User, Message, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()

class MessageModelTestCase(TestCase):
    """ Test Message models """
    def setUp(self):
        """ Create test users and messages """
        Message.query.delete()
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)

        db.session.commit()
        self.u1_id = u1.id
        self.u2_id = u2.id

        m1 = Message(text='message1', user_id = self.u1_id)
        m2 = Message(text='message2', user_id = self.u2_id)

        db.session.add(m1)
        db.session.add(m2)
        db.session.commit()
        self.m1_id = m1.id
        self.m2_id = m2.id

        self.client = app.test_client()

    def tearDown(self):
        """ Clean up any fouled transactions """
        db.session.rollback()

    def test_message_model(self):
        """ Test that the message relationships are as intended """
        m1 = Message.query.get(self.m1_id)
        u1 = User.query.get(self.u1_id)
        
        self.assertEqual(len(u1.messages), 1)
        self.assertEqual(len(m1.users_liked), 0) # could do this separately
        self.assertEqual(u1.messages[0], 'message1')
        

    def test_delete_message(self):
        """ Test deleting a message """
        m1 = Message.query.get(self.m1_id)
        db.session.delete(m1) # need this to make changes (not committed though)
        # db.session.commit()  don't need to commit in test because you can already access changes

        self.assertNotIn(m1, Message.query.all())
    
    def test_add_message(self):
        """ Test adding a message """
        m3 = Message(text='message3', user_id = self.u2_id)
        db.session.add(m3)
        
        self.assertIn(m3, Message.query.all()) # instead of checking entire object, can check its values

        #a bunch of self.assertEqual(m3.text = 'message1')

        
        # try:
        #     bad_message = Message(user_id = self.u2_id)

        # except:
        #     all_messages = Message.query.all()
        #     self.assertNotIn(bad_message, all_messages)

        #TODO: put this in different test and do the same with self.assertRaises(IntegrityError)

    def test_number_liked(self):
        """ Test that the number_liked relationship works as intended """
        m1 = Message.query.get(self.m1_id)
        u2 = User.query.get(self.u2_id)

        m1.users_liked.append(u2)

        self.assertIn(u2, m1.users_liked)