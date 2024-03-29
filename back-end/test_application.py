from flask_testing import TestCase
from application import app, db, User, Clip, Comment
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

    def testDeleteClipWithComments_commentsAlsoDeleted(self):
        clipUuid = str(uuid.uuid4())
        db.session.add(self.createClip(id=5, authorId=7, title="HIKO ARE YOU KIDDING ME", clipUuid=clipUuid))
        db.session.add(Comment(comment="Nice", id=1, authorId=2, clipId=5))
        db.session.commit()
        clipPath = Clip.getClipPath(clipUuid)

        testClip = open(clipPath, "w")
        testClip.write("ASDF")
        testClip.close()
        assert os.path.isfile(clipPath)

        # This fails unless comments are also deleted upon clip deletion, due to the following error:
        # sqlalchemy.exc.IntegrityError: (sqlite3.IntegrityError) NOT NULL constraint failed: comment.clipId
        response = self.client.delete("/clips/5")

        assert response.status_code == 200
        assert os.path.isfile(Clip.getClipPath(clipUuid)) == False
        assert Comment.query.get(1) is None

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

class GetClipInformation(BaseTestCase):
    def testGetExistingClipInformation(self):
        db.session.add(self.createUser())
        db.session.add(self.createClip(id=5, authorId=1, title="CSGO ACE", dateOfCreation=datetime.min, description="asdfgg"))
        db.session.commit()

        response = self.client.get("/clips/info/5")

        assert response.status_code == 200
        assert len(response.json) == 5
        assert response.json["title"] == "CSGO ACE"
        assert response.json["description"] == "asdfgg"
        assert response.json["date"] == str(datetime.min)
        assert response.json["author"] == "bob"
        assert response.json["authorId"] == 1

    def testGetNonexistantClipInformation(self):
        response = self.client.get("/clips/info/5")

        assert response.status_code == 404

class AddComment(BaseTestCase):
    def testAddValidComment(self):
        db.session.add(self.createUser())
        db.session.add(self.createClip(id=5, authorId=1, title="CSGO ACE", dateOfCreation=datetime.min, description="asdfgg"))
        db.session.add(User(id=2, username="tempuser", password="asdf"))

        response = self.client.put("/comments/5", json=dict(authorId=2, comment="nice ace"))
        commentInDatabase = Comment.query.filter_by(id=1).first()

        assert response.status_code == 200

        assert commentInDatabase.comment == "nice ace"
        assert commentInDatabase.clipId == 5
        assert commentInDatabase.authorId == 2

    def testInvalidClipId(self):
        db.session.add(self.createUser())

        response = self.client.put("/comments/5", json=dict(authorId=1, comment="nice ace"))

        assert response.status_code == 404
        assert response.json["status"] == "Clip doesn't exist."

    def testNoAuthorId(self):
        db.session.add(self.createUser())
        db.session.add(self.createClip(id=5, authorId=1, title="CSGO ACE", dateOfCreation=datetime.min, description="asdfgg"))

        response = self.client.put("/comments/5", json=dict(comment="nice ace"))

        assert response.status_code == 400
        assert response.json["status"] == "No author id included."

    def testInvalidAuthor(self):
        db.session.add(self.createUser())
        db.session.add(self.createClip(id=5, authorId=1, title="CSGO ACE", dateOfCreation=datetime.min, description="asdfgg"))

        response = self.client.put("/comments/5", json=dict(authorId=2, comment="nice ace"))

        assert response.status_code == 404
        assert response.json["status"] == "Author doesn't exist"

    def testNoComment(self):
        db.session.add(self.createUser())
        db.session.add(self.createClip(id=5, authorId=1, title="CSGO ACE", dateOfCreation=datetime.min, description="asdfgg"))
        db.session.add(User(id=2, username="tempuser", password="asdf"))

        response = self.client.put("/comments/5", json=dict(authorId=2))

        assert response.status_code == 400
        assert response.json["status"] == "No comment added."

    def testNoBodyInComment(self):
        db.session.add(self.createUser())
        db.session.add(self.createClip(id=5, authorId=1, title="CSGO ACE", dateOfCreation=datetime.min, description="asdfgg"))
        db.session.add(User(id=2, username="tempuser", password="asdf"))

        response = self.client.put("/comments/5", json=dict(authorId=2, comment=""))
        
        assert response.status_code == 400
        assert response.json["status"] == "No comment body included."

class GetComments(BaseTestCase):
    def testGetValidClipWithComments(self):
        db.session.add(self.createUser())
        db.session.add(self.createClip(id=5, authorId=1, title="CSGO ACE", dateOfCreation=datetime.min, description="asdfgg"))
        db.session.add(User(id=2, username="tempuser", password="asdf"))
        db.session.add(Comment(comment="Nice", authorId=2, clipId=5, dateOfCreation=datetime.max))
        db.session.add(Comment(comment="thanks", authorId=1, clipId=5, dateOfCreation=datetime.min))
        db.session.commit()

        response = self.client.get("/comments/5")

        assert response.status_code == 200
        assert len(response.json) == 2

        assert response.json[0]["comment"] == "Nice"
        assert response.json[0]["author"] == "tempuser"
        assert response.json[0]["date"] == str(datetime.max)
        assert response.json[0]["authorId"] == 2

        assert response.json[1]["comment"] == "thanks"
        assert response.json[1]["author"] == "bob"
        assert response.json[1]["date"] == str(datetime.min)
        assert response.json[1]["authorId"] == 1

    def testGetValidClipWithNoComments(self):
        db.session.add(self.createUser())
        db.session.add(self.createClip(id=5, authorId=1, title="CSGO ACE", dateOfCreation=datetime.min, description="asdfgg"))
        db.session.commit()

        response = self.client.get("/comments/5")

        assert response.status_code == 200
        assert len(response.json) == 0

    def testGetInvalidClipComments(self):
        response = self.client.get("/comments/5")

        assert response.status_code == 404

class IsFollowing(BaseTestCase):
    def testFollowingUser(self):
        follower = self.createUser()
        followee = User(id=2, username="tempuser", password="asdf")
        db.session.add(follower)
        db.session.add(followee)
        follower.followed.append(followee)
        db.session.commit()

        response = self.client.get(f"/follow/{follower.id}/{followee.id}")

        assert response.status_code == 200
        assert response.json["following"] == True

    def testNotFollowingUser(self):
        follower = self.createUser()
        followee = User(id=2, username="tempuser", password="asdf")
        db.session.add(follower)
        db.session.add(followee)
        db.session.commit()

        response = self.client.get(f"/follow/{follower.id}/{followee.id}")

        assert response.status_code == 200
        assert response.json["following"] == False

    def testNotExistingFollower(self):
        followee = User(id=2, username="tempuser", password="asdf")
        db.session.add(followee)
        db.session.commit()

        response = self.client.get(f"/follow/1/{followee.id}")

        assert response.status_code == 404
        assert response.json["status"] == "Current user (follower) does not exist"

    def testNotExistingFollowee(self):
        follower = self.createUser()
        db.session.add(follower)
        db.session.commit()

        response = self.client.get(f"/follow/{follower.id}/2")

        assert response.status_code == 404
        assert response.json["status"] == "Other user (followee) does not exist"

    def testIsFollowingOneself(self):
        user = self.createUser()
        db.session.add(user)
        db.session.commit()

        response = self.client.get(f"/follow/{user.id}/{user.id}")

        assert response.status_code == 400
        assert response.json["status"] == "You can't follow/unfollow yourself"

class Follow(BaseTestCase):
    def testFollowValid(self):
        follower = self.createUser()
        followee = User(id=2, username="tempuser", password="asdf")
        db.session.add(follower)
        db.session.add(followee)
        db.session.commit()

        response = self.client.put(f"/follow/{follower.id}/{followee.id}")

        assert response.status_code == 200
        assert response.json["following"] == True
        assert follower.followed.count() == 1

    def testFollowInvalid(self):
        follower = self.createUser()
        followee = User(id=2, username="tempuser", password="asdf")
        db.session.add(follower)
        db.session.add(followee)
        follower.followed.append(followee)
        db.session.commit()

        response = self.client.put(f"/follow/{follower.id}/{followee.id}")

        assert response.status_code == 200
        assert response.json["following"] == True

    def testNotExistingFollower(self):
        followee = User(id=2, username="tempuser", password="asdf")
        db.session.add(followee)
        db.session.commit()

        response = self.client.put(f"/follow/1/{followee.id}")

        assert response.status_code == 404
        assert response.json["status"] == "Current user (follower) does not exist"

    def testNotExistingFollowee(self):
        follower = self.createUser()
        db.session.add(follower)
        db.session.commit()

        response = self.client.put(f"/follow/{follower.id}/2")

        assert response.status_code == 404
        assert response.json["status"] == "Other user (followee) does not exist"

    def testFollowOneself(self):
        user = self.createUser()
        db.session.add(user)
        db.session.commit()

        response = self.client.put(f"/follow/{user.id}/{user.id}")

        assert response.status_code == 400
        assert response.json["status"] == "You can't follow/unfollow yourself"

class Unfollow(BaseTestCase):
    def testUnfollowValid(self):
        follower = self.createUser()
        followee = User(id=2, username="tempuser", password="asdf")
        db.session.add(follower)
        db.session.add(followee)
        follower.followed.append(followee)
        db.session.commit()

        response = self.client.delete(f"/follow/{follower.id}/{followee.id}")

        assert response.status_code == 200
        assert response.json["following"] == False
        assert follower.followed.count() == 0

    def testFollowInvalid(self):
        follower = self.createUser()
        followee = User(id=2, username="tempuser", password="asdf")
        db.session.add(follower)
        db.session.add(followee)
        db.session.commit()

        response = self.client.delete(f"/follow/{follower.id}/{followee.id}")

        assert response.status_code == 200
        assert response.json["following"] == False

    def testNotExistingFollower(self):
        followee = User(id=2, username="tempuser", password="asdf")
        db.session.add(followee)
        db.session.commit()

        response = self.client.delete(f"/follow/1/{followee.id}")

        assert response.status_code == 404
        assert response.json["status"] == "Current user (follower) does not exist"

    def testNotExistingFollowee(self):
        follower = self.createUser()
        db.session.add(follower)
        db.session.commit()

        response = self.client.delete(f"/follow/{follower.id}/2")

        assert response.status_code == 404
        assert response.json["status"] == "Other user (followee) does not exist"

    def testUnfollowOneself(self):
        user = self.createUser()
        db.session.add(user)
        db.session.commit()

        response = self.client.delete(f"/follow/{user.id}/{user.id}")

        assert response.status_code == 400
        assert response.json["status"] == "You can't follow/unfollow yourself"

class GetFollowFeed(BaseTestCase):
    def testValidPopulatedFollowFeed(self):
        follower = self.createUser()
        followee = User(id=2, username="tempuser", password="asdf")
        db.session.add(follower)
        db.session.add(followee)
        follower.followed.append(followee)
        db.session.add(self.createClip(id=5, authorId=2, title="CSGO ACE", dateOfCreation=datetime.min))
        db.session.add(self.createClip(id=155, authorId=2, title="VALORANT NINJA DEFUSE", dateOfCreation=datetime.max))
        db.session.add(self.createClip(id=15515, authorId=5, title="ROBLOX HIGHLIGHTS WOW"))  # this is just to test that it doesn't return unneccessary clips.
        db.session.commit()

        response = self.client.get(f"/follow/clips/{follower.id}")

        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) == 2
        assert 155 == response.json[0]
        assert 5 == response.json[1]

    def testValidUnpopulatedFollowFeed(self):
        follower = self.createUser()
        followee = User(id=2, username="tempuser", password="asdf")
        db.session.add(follower)
        db.session.add(followee)
        follower.followed.append(followee)
        db.session.commit()

        response = self.client.get(f"/follow/clips/{follower.id}")

        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) == 0

    def testUserDoesntExist(self):
        response = self.client.get(f"/follow/clips/1")

        assert response.status_code == 404
        assert response.json["status"] == "User does not exist"

class GetUser(BaseTestCase):
    def testValidUserWithClips(self):
        db.session.add(self.createUser())
        db.session.add(self.createClip(id=5, authorId=1, title="CSGO ACE", dateOfCreation=datetime.min))
        db.session.add(self.createClip(id=155, authorId=1, title="VALORANT NINJA DEFUSE", dateOfCreation=datetime.max))
        db.session.commit()

        response = self.client.get("/user/1")

        assert response.status_code == 200
        assert response.json["user"] == "bob"
        assert response.json["numClips"] == 2

    def testValidUserWithNoClips(self):
        db.session.add(self.createUser())
        db.session.commit()

        response = self.client.get("/user/1")

        assert response.status_code == 200
        assert response.json["user"] == "bob"
        assert response.json["numClips"] == 0

    def testInvalidUser(self):
        response = self.client.get("/user/1")

        assert response.status_code == 404
