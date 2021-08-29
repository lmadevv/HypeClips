from flask_testing import TestCase
from application import app, db, User

class BaseUserTestCase(TestCase):
    """
    Test case class that all test cases should extend.
    This class handles setting up the test Flask app and test database.

    DO NOT MODIFY THIS CLASS
    """
    def create_app(self):
        """Creates the test Flask app and database."""
        test_app = app
        test_app.config["TESTING"] = True
        test_app.config["DEBUG"] = False
        test_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://" # Creates an in-memory database for testing
        db.init_app(test_app)
        return test_app

    def setUp(self):
        """Automatically called before the start of any singular test case."""
        # Create a fresh database before running any test.
        db.create_all()

    def tearDown(self):
        """Automatically called after the end of any singular test case."""
        # Clear out the database after running any test.
        db.session.remove()
        db.drop_all()

    def createUser(self):
        return User(username="bob", password="pass123")

class UserLogin(BaseUserTestCase):
    """
    Tests for the /login endpoint.
    """

    def testValidLogin(self):

        db.session.add(self.createUser())
        db.session.commit()

        response = self.client.post("/login", json=dict(username="bob", password="pass123"))

        assert response.status_code == 200

    def testInvalidLoginWrongUsername(self):

        db.session.add(self.createUser())
        db.session.commit()

        response = self.client.post("/login", json=dict(username="boasdb", password="pass123"))

        assert response.status_code == 404
        assert response.json["status"] == "not a valid login"

    def testInvalidLoginWrongPassword(self):

        db.session.add(self.createUser())
        db.session.commit()

        response = self.client.post("/login", json=dict(username="bob", password="pass123asdasd"))

        assert response.status_code == 404
        assert response.json["status"] == "not a valid login"

class UserRegister(BaseUserTestCase):
    """
    Tests for the /register endpoint.
    """

    def testValidRegistration(self):

        response = self.client.post("/register", json=dict(username="bob", password="pass123"))

        assert response.status_code == 200

        user = User.query.get(1)

        assert user.username == "bob"
        assert user.password == "pass123"

    def testInvalidRegistrationAlreadyRegistered(self):

        db.session.add(self.createUser())
        db.session.commit()

        response = self.client.post("/register", json=dict(username="bob", password="123123"))

        assert response.status_code == 400
        assert response.json["status"] == "unsuccessful registration: user with username already exists"

    def testInvalidRegistrationLongUsername(self):

        db.session.add(self.createUser())
        db.session.commit()

        response = self.client.post("/register", json=dict(
            username="basdkjfasdjflkjasdflkjaskfdjaslkdfjlskadjflkasjdflkjadflkasjklfsfob", password="123123"))

        assert response.status_code == 400
        assert response.json["status"] == "unsuccessful registration: username too long"

    def testInvalidRegistrationLongPassword(self):

        db.session.add(self.createUser())
        db.session.commit()

        response = self.client.post("/register", json=dict(username="bob34",
                                                                password="123121231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231233"))

        assert response.status_code == 400
        assert response.json["status"] == "unsuccessful registration: password too long"

