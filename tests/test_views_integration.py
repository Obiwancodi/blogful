import os
import unittest
from urlparse import urlparse

from werkzeug.security import generate_password_hash

# Configure your app to use the testing database
os.environ["CONFIG_PATH"] = "blog.config.TestingConfig"

from blog import app
from blog import models
from blog.database import Base, engine, session
from werkzeug.contrib.fixers import LighttpdCGIRootFix
app.wsgi_app = LighttpdCGIRootFix(app.wsgi_app)

class TestViews(unittest.TestCase):
    def setUp(self):
        """ Test setup """
        self.client = app.test_client()

        # Set up the tables in the database
        Base.metadata.create_all(engine)

        # Create an example user
        self.user = models.User(name="Alice", email="alice@example.com",
                                password=generate_password_hash("test"))
        session.add(self.user)
        session.commit()

    def tearDown(self):
        """ Test teardown """
        session.close()
        # Remove the tables and their data from the database
        Base.metadata.drop_all(engine)
        
    def simulate_login(self):
        with self.client.session_transaction() as http_session:
            http_session["user_id"] = str(self.user.id)
            http_session["_fresh"] = True

    def testAddPost(self):
        self.simulate_login()

        response = self.client.post("/post/add", data={
            "title": "Test Post",
            "content": "Test content"
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, "/")
        posts = session.query(models.Post).all()
        self.assertEqual(len(posts), 1)

        post = posts[0]
        self.assertEqual(post.title, "Test Post")
        self.assertEqual(post.content, "<p>Test content</p>\n")
        self.assertEqual(post.author, self.user)
       
    def testEditPost(self):
        self.simulate_login()
        
        response = self.client.post("/post/add", data={
                "title": "Test Post",
                "content": "Test content"
            })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, "/")
        posts = session.query(models.Post).all()
        post = posts[0]
        
        response = self.client.post("/post/" + str(posts[0].id) + "/edit", data={
                "title": "Edit Post",
                "content": "Edit content"
            })
        self.assertEqual(response.status_code,302)
        self.assertEqual(post.title, "Edit Post")
        self.assertEqual(post.content, "<p>Edit content</p>\n")
        self.assertEqual(len(posts), 1)
        self.assertEqual(post.author, self.user)
        
    def testDeletePost(self):
        self.simulate_login()
        
        response = self.client.post("/post/add", data={
               "title": "Test Post",
               "content": "Test content"
            })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, "/")
        posts = session.query(models.Post).all()
        post = posts[0]
        self.assertEqual(len(posts), 1)
        
        response = self.client.post("/post/" + str(posts[0].id) + "/delete", data={
                "title": "",
                "content": ""
            })
        posts = session.query(models.Post).all()
        self.assertEqual(response.status_code,302)
        self.assertEqual(len(posts),0)
        
if __name__ == "__main__":
    unittest.main()