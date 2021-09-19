from flask_testing import TestCase
from application import app, db, User, Clip
import os, io, uuid

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

    def testValidLogin(self):

        db.session.add(self.createUser())
        db.session.commit()

        response = self.client.post("/login", json=dict(username="bob", password="pass123"))

        assert response.status_code == 200
        assert response.json['id'] == 1

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

    def testValidRegistration(self):

        response = self.client.post("/register", json=dict(username="bob", password="pass123"))

        assert response.status_code == 200

        user = User.query.get(1)

        assert user.username == "bob"
        assert user.password == "pass123"
        assert response.json['id'] == 1

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

class AddClips(BaseUserTestCase):

    def testValidAddedClip(self):

        response = self.client.put("/clips", data={"file": (io.BytesIO(b"this is a test"), "test.mp4")})

        assert response.status_code == 200
        clip = Clip.query.get(1)
        assert response.json["id"] == clip.id

        fullClipPath = os.path.join(os.path.join(os.getcwd(), "clips"), f"{clip.clipUuid}.mp4")
        os.remove(fullClipPath)

    def testNoFilePartAdded(self):

        response = self.client.put("clips")

        assert response.status_code == 400
        assert response.json["status"] == "no file part added to the request"

    def testWrongFileExtensionAdded(self):

        response = self.client.put("clips", data={"file": (io.BytesIO(b"this is a test"), "test.pdf")})

        assert response.status_code == 400
        assert response.json["status"] == "the file had the wrong format"

class GetClipIds(BaseUserTestCase):

    def testGetClipIds(self):

        db.session.add(Clip(id=5, clipUuid="f7e49c9a-b90b-4d1d-ad3a-309203f0503d"))
        db.session.add(Clip(id=7, clipUuid="3aacf6bb-1a8d-40f9-ab17-d399a082f633"))

        response = self.client.get('/clips')

        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) == 2
        assert 5 in response.json
        assert 7 in response.json

    def testGetClipIdsEmpty(self):

        response = self.client.get('/clips')

        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) == 0

class GetClipById(BaseUserTestCase):

    def testGetClipByValidId(self):

        # TODO IM NOT REALLY SURE HOW TO DO THIS TEST ?

        clipUuid = str(uuid.uuid4())
        db.session.add(Clip(id=5, clipUuid=clipUuid))
        clipPath = os.path.join(os.path.join(os.getcwd(), "clips"), f"{clipUuid}.mp4")

        testClip = open(clipPath, "w")
        testClip.write("ASDF")
        testClip.close()

        response = self.client.get('/clips/5')

        assert response.status_code == 200
        assert response.data == b"ASDF"

        response.close()
        os.remove(clipPath)

    def testGetClipByInvalidId(self):

        response = self.client.get('/clips/5')

        assert response.status_code == 404
