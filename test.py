#!/usr/bin/env python

from datetime import datetime, timedelta
import unittest
from config import Config
from app import create_app, db
from app.models import User, Post


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///"


class UserModelCase(unittest.TestCase):
    def setup(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        u = User(username="Bilal")
        u.set_password("cat")
        self.assertFalse(u.check_password("dog"))
        self.assertTrue(u.check_password("cat"))

    def test_avatar(self):
        u = User(username="King", email="bilal_khan786@live.com")
        self.assertEqual(
            u.avatar(128),
            (
                "https://www.gravatar.com/avatar/14754049ceef6889bee881e4346de7d5?id=identicon&s=128"
            ),
        )

    def test_follow(self):
        u1 = User(username="john", email="john@example.com")
        u2 = User(username="wick", email="wick@example.com")
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u1.followers.all(), [])

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, "wick")
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username, "john")

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u2.followers.count(), 0)

    def test_follow_posts(self):
        # create four users
        u1 = User(username="john", email="john@example.com")
        u2 = User(username="susan", email="susan@example.com")
        u3 = User(username="mary", email="mary@example.com")
        u4 = User(username="david", email="david@example.com")
        db.session.add_all([u1, u2, u3, u4])

        # create four posts
        now = datetime.utcnow()

        p1 = Post(
            body="Post from John", author=u1, timestamp=now + timedelta(seconds=1)
        )
        p2 = Post(
            body="POst from susan", author=u2, timestamp=now + timedelta(seconds=4)
        )
        p3 = Post(
            body="Post from mary", author=u3, timestamp=now + timedelta(seconds=3)
        )
        p4 = Post(
            body="Post from david", author=u4, timestamp=now + timedelta(seconds=2)
        )
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        # setup the followers

        u1.follow(u2)  # John follow susan
        u1.follow(u4)  # John follow david
        u2.follow(u3)  # Susan follow mary
        u3.follow(u4)  # mary follow susan
        db.session.commit()

        # check the followed posts of each user
        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()
        self.assertEqual(f1, [p2, p4, p1])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])


if __name__ == "__main__":
    unittest.main(verbosity=2)
