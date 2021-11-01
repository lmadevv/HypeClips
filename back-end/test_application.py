from flask_testing import TestCase
from application import app, db, User, Clip
from datetime import datetime
import os, io, uuid

class BaseTestCase(TestCase):
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

    def createClip(self, id, authorId, clipUuid=str(uuid.uuid4()), title="Default clip title", description="", dateOfCreation=datetime.utcnow()):
        return Clip(id=id, authorId=authorId, clipUuid=clipUuid, title=title, description=description, dateOfCreation=dateOfCreation)

class UserLogin(BaseTestCase):

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

class UserRegister(BaseTestCase):

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

class AddClips(BaseTestCase):

    def testValidAddedClip(self):

        response = self.client.put("/clips", data={"file": (io.BytesIO(b"this is a test"), "test.mp4"), "authorId": 52, "title": "Bob sick league clip!"})

        assert response.status_code == 200
        clip = Clip.query.get(1)
        assert response.json["id"] == clip.id
        assert clip.authorId == 52
        assert clip.title == "Bob sick league clip!"
        assert clip.description == ""
        try:
            uuid.UUID(clip.clipUuid, version=4)
        except ValueError:
            assert False

        os.remove(Clip.getClipPath(clip.clipUuid))

    def testNoFilePartAdded(self):

        response = self.client.put("clips")

        assert response.status_code == 400
        assert response.json["status"] == "no file part added to the request"

    def testWrongFileExtensionAdded(self):

        response = self.client.put("clips", data={"file": (io.BytesIO(b"this is a test"), "test.pdf"), "authorId": 52, "title": "Bob sick league clip!"})

        assert response.status_code == 400
        assert response.json["status"] == "the file had the wrong format"

    def testNoAuthorIdIncluded(self):

        response = self.client.put("clips", data={"file": (io.BytesIO(b"this is a test"), "test.pdf"), "title": "Bob sick league clip!"})

        assert response.status_code == 400
        assert response.json["status"] == "no author id included"

    def testNoTitleIncluded(self):

        response = self.client.put("clips", data={"file": (io.BytesIO(b"this is a test"), "test.pdf"), "authorId": 52})

        assert response.status_code == 400
        assert response.json["status"] == "no title included"

class GetClipIds(BaseTestCase):

    def testGetClipIds(self):

        db.session.add(self.createClip(id=5, authorId=2, title="WHAT A FLICK!", dateOfCreation=datetime.min))
        db.session.add(self.createClip(id=7, authorId=5, title="DUNK ON NBA", dateOfCreation=datetime.max))
        db.session.commit()

        response = self.client.get("/clips")

        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) == 2
        assert 7 == response.json[0]
        assert 5 == response.json[1]


    def testGetClipIdsEmpty(self):

        response = self.client.get("/clips")

        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) == 0

class GetClipById(BaseTestCase):

    def testGetClipByValidId(self):

        clipUuid = str(uuid.uuid4())
        db.session.add(self.createClip(id=5, authorId=7, title="HIKO ARE YOU KIDDING ME", clipUuid=clipUuid))
        db.session.commit()
        clipPath = Clip.getClipPath(clipUuid)

        testClip = open(clipPath, "w")
        testClip.write("ASDF")
        testClip.close()

        response = self.client.get("/clips/5")

        assert response.status_code == 200
        assert response.data == b"ASDF"

        # Close the response in order to delete the temporary clip created. Without closing it wouldn't delete since
        # the response keeps the file open. This ensures the file gets closed so we can delete it.
        response.close()
        os.remove(clipPath)

    def testGetClipByInvalidId(self):

        response = self.client.get("/clips/5")

        assert response.status_code == 404

class DeleteClip(BaseTestCase):

    def testDeleteValidClip(self):

        clipUuid = str(uuid.uuid4())
        db.session.add(self.createClip(id=5, authorId=7, title="HIKO ARE YOU KIDDING ME", clipUuid=clipUuid))
        db.session.commit()
        clipPath = Clip.getClipPath(clipUuid)

        testClip = open(clipPath, "w")
        testClip.write("ASDF")
        testClip.close()
        assert os.path.isfile(clipPath)

        response = self.client.delete("/clips/5")

        assert response.status_code == 200
        assert os.path.isfile(Clip.getClipPath(clipUuid)) == False
        assert self.client.delete("/clips/5").status_code == 404

    def testDeleteInvalidClip(self):

        response = self.client.delete("/clips/5")

        assert response.status_code == 404

class GetClipIdsForAuthor(BaseTestCase):

    def testGetExistingClipIds(self):

        db.session.add(self.createUser())
        db.session.add(self.createClip(id=5, authorId=1, title="CSGO ACE", dateOfCreation=datetime.min))
        db.session.add(self.createClip(id=155, authorId=1, title="VALORANT NINJA DEFUSE", dateOfCreation=datetime.max))

        # this is just to test that it doesn't return unneccessary clips.
        db.session.add(self.createClip(id=15515, authorId=5, title="ROBLOX HIGHLIGHTS WOW"))
        db.session.commit()

        response = self.client.get("/1/clips")

        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) == 2
        assert 155 == response.json[0]
        assert 5 == response.json[1]

    def testGetNonexistantClipIds(self):

        db.session.add(self.createUser())
        db.session.commit()

        response = self.client.get("/1/clips")

        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) == 0