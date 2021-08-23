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
        test_app.config['TESTING'] = True
        test_app.config['DEBUG'] = False
        test_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://' # Creates an in-memory database for testing
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
        """
        Tests that login works for a valid username
        """
        # Set up all the data needed
        db.session.add(self.createUser())
        db.session.commit()

        # Call the login method
        response = self.client.post('/login', json=dict(username="bob", password="pass123"))

        # Check if the response is what we wanted
        assert response.status_code == 200
        assert response.json['status'] == "successful login"

    def testInvalidLogin(self):
        """
        Tests that login works for a valid username
        """
        # Set up all the data needed
        db.session.add(self.createUser())
        db.session.commit()

        # Call the login method with invalid name and wrong password
        responseOne = self.client.post('/login', json=dict(username="boasdb", password="pass123"))
        responseTwo = self.client.post('/login', json=dict(username="bob", password="pass123asdasd"))

        # Check if the responses is what we wanted
        assert responseOne.status_code == 401
        assert responseOne.json['status'] == "not a valid login"
        assert responseTwo.status_code == 401
        assert responseTwo.json['status'] == "not a valid login"

class UserRegister(BaseUserTestCase):
    """
    Tests for the /register endpoint.
    """

    def testValidRegistration(self):
        """
        Tests for a valid registration
        """
        # Call the register method
        response = self.client.post('/register', json=dict(username="bob", password="pass123"))

        # Check if the response is what we wanted
        assert response.status_code == 200
        assert response.json['status'] == "successful registration"

        # Get the user from the database
        user = User.query.get(1)

        # Check if the info is the original info
        assert user.username == "bob"
        assert user.password == "pass123"

    def testInvalidRegistration(self):
        """
        Tests for invalid registrations
        """
        # Set up all the data needed
        db.session.add(self.createUser())
        db.session.commit()

        # Call the register methods with 1) same username, 2) too long username, 3) too long password
        responseOne = self.client.post('/register', json=dict(username="bob", password="123123"))
        responseTwo = self.client.post('/register', json=dict(username="basdkjfasdjflkjasdflkjaskfdjaslkdfjlskadjflkasjdflkjadflkasjklfsfob", password="123123"))
        responseThree = self.client.post('/register', json=dict(username="bob34", password="123121231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231231233"))

        # Check if the response is what we wanted
        assert responseOne.status_code == 400
        assert responseOne.json['status'] == "unsuccessful registration: user with username already exists"
        assert responseTwo.status_code == 400
        assert responseTwo.json['status'] == "unsuccessful registration: username too long"
        assert responseThree.status_code == 400
        assert responseThree.json['status'] == "unsuccessful registration: password too long"
