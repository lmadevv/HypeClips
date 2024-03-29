from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid, os

EMPTY_RESPONSE = ""

app = Flask(__name__)
# Enable CORS so that front-end requests work when testing locally 
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

followers = db.Table('followers',
    db.Column('followerId', db.Integer, db.ForeignKey('user.id')),
    db.Column('followedId', db.Integer, db.ForeignKey('user.id'))
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(40), nullable=False)
    clips = db.relationship("Clip", backref="author", lazy=True)
    comments = db.relationship("Comment", backref="author", lazy=True)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.followerId == id),
        secondaryjoin=(followers.c.followedId == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def follow(self, user):
        isNotFollowing = not self.isFollowing(user)
        if isNotFollowing:
            self.followed.append(user)
        return isNotFollowing

    def unfollow(self, user):
        isFollowing = self.isFollowing(user)
        if isFollowing:
            self.followed.remove(user)
        return isFollowing

    def isFollowing(self, user):
        return self.followed.filter(
            followers.c.followedId == user.id).count() > 0

    def followedClips(self):
        return Clip.query.join(
            followers, (followers.c.followedId == Clip.authorId)).filter(
            followers.c.followerId == self.id).order_by(
            Clip.dateOfCreation.desc())

class Clip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    clipUuid = db.Column(db.String(100), nullable=False)
    authorId = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    dateOfCreation = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    title = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(200))
    # Ensure cascade="all,delete" exists on this field, so that a Clip with Comments can be deleted 
    # without breaking the database from leftover Comment models containing a null clipId
    # https://stackoverflow.com/q/5033547
    comments = db.relationship("Comment", cascade="all,delete", backref="clip", lazy=True)

    @staticmethod
    def getClipPath(uuid):
        return os.path.join(os.path.join(os.getcwd(), "clips"), f"{uuid}.mp4")

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(200), nullable=False)
    dateOfCreation = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    authorId = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    clipId = db.Column(db.Integer, db.ForeignKey("clip.id"), nullable=False)

def errorMessageWithCode(status, code):
    return {"status": status}, code

def followChecks(follower, followee):
    if follower is None:
        return errorMessageWithCode("Current user (follower) does not exist", 404)
    if followee is None:
        return errorMessageWithCode("Other user (followee) does not exist", 404)
    if follower.id == followee.id:
        return errorMessageWithCode("You can't follow/unfollow yourself", 400)
    return True     # if all the checks pass we return true for everything checks out

@app.route("/login", methods=["POST"])
def login():
    user = User.query.filter_by(username=request.json["username"], password=request.json["password"]).first()

    if user != None:
        return {"id": user.id}
    else:
        return errorMessageWithCode("not a valid login", 404)

@app.route("/register", methods=["POST"])
def register():
    user = User.query.filter_by(username=request.json["username"]).first()

    if user != None:
        return errorMessageWithCode("unsuccessful registration: user with username already exists", 400)

    if len(request.json["username"]) > 20:
        return errorMessageWithCode("unsuccessful registration: username too long", 400)

    if len(request.json["password"]) > 40:
        return errorMessageWithCode("unsuccessful registration: password too long", 400)

    newUser = User(username=request.json["username"], password=request.json["password"])
    db.session.add(newUser)
    db.session.commit()

    return {"id": newUser.id}

@app.route("/clips")
def getClipIds():
    clips = Clip.query.order_by(Clip.dateOfCreation.desc()).all()

    output = []
    for clip in clips:
        output.append(clip.id)

    return jsonify(output)

@app.route("/clips", methods=["PUT"])
def addClips():
    if "file" not in request.files:
        return errorMessageWithCode("no file part added to the request", 400)
    file = request.files["file"]

    if request.form.get("authorId") is None:
        return errorMessageWithCode("no author id included", 400)

    if request.form.get("title") is None:
        return errorMessageWithCode("no title included", 400)

    description = request.form.get("description")
    if description is None:
        description = ""


    # TODO: Check if the file is in a video format instead of the file extension
    # This will require us to change the tests if this change does go through
    if file.filename.split(".")[1].lower() != "mp4":
        return errorMessageWithCode("the file had the wrong format", 400)

    clipsPath = os.path.join(os.getcwd(), "clips")
    if not os.path.exists(clipsPath):
        os.mkdir(clipsPath)

    clipUuid = str(uuid.uuid4())
    fullPath = Clip.getClipPath(clipUuid)
    file.save(fullPath)

    newClip = Clip(clipUuid=clipUuid, authorId=int(request.form.get("authorId")), title=request.form.get("title"), description=description)
    db.session.add(newClip)
    db.session.commit()

    return {"id": newClip.id}

@app.route("/clips/<clipid>")
def getClipById(clipid):
    clip = Clip.query.get_or_404(clipid)

    return send_file(Clip.getClipPath(clip.clipUuid), mimetype="application/mp4")

@app.route("/clips/<clipid>", methods=["DELETE"])
def deleteClip(clipid):
    clip = Clip.query.get_or_404(clipid)

    os.remove(Clip.getClipPath(clip.clipUuid))
    db.session.delete(clip)
    db.session.commit()

    return EMPTY_RESPONSE

@app.route("/comments/<clipid>")
def getComments(clipid):
    Clip.query.get_or_404(clipid)

    comments = Comment.query.order_by(Comment.dateOfCreation.desc()).filter_by(clipId=clipid).all()
    returnComments = []

    for comment in comments:
        returnComments.append({"author": comment.author.username, "comment": comment.comment, "date": str(comment.dateOfCreation), "authorId": comment.author.id})

    return jsonify(returnComments)

@app.route("/comments/<clipid>", methods=["PUT"])
def addComment(clipid):
    if Clip.query.get(clipid) is None:
        return errorMessageWithCode("Clip doesn't exist.", 404)
    if "authorId" not in request.json:
        return errorMessageWithCode("No author id included.", 400)
    if User.query.get(request.json["authorId"]) is None:
        return errorMessageWithCode("Author doesn't exist", 404)
    if "comment" not in request.json:
        return errorMessageWithCode("No comment added.", 400)
    if request.json["comment"] == "":
        return errorMessageWithCode("No comment body included.", 400)

    db.session.add(Comment(comment=request.json["comment"], authorId=request.json["authorId"], clipId=clipid))
    db.session.commit()

    return EMPTY_RESPONSE

@app.route("/user/<userid>")
def getUser(userid):
    user = User.query.get_or_404(userid)

    return {"user": user.username, "numClips": len(user.clips)}

@app.route("/follow/<followerId>/<followeeId>")
def isFollowing(followerId, followeeId):
    follower = User.query.get(followerId)
    followee = User.query.get(followeeId)
    result = followChecks(follower, followee)

    if result == True:
        return {"following": follower.isFollowing(followee)}
    return result

@app.route("/follow/<followerId>/<followeeId>", methods=["PUT"])
def follow(followerId, followeeId):
    follower = User.query.get(followerId)
    followee = User.query.get(followeeId)
    result = followChecks(follower, followee)

    if result == True:
        follower.follow(followee)
        db.session.commit()
        return {"following": True}
    return result

@app.route("/follow/<followerId>/<followeeId>", methods=["DELETE"])
def unfollow(followerId, followeeId):
    follower = User.query.get(followerId)
    followee = User.query.get(followeeId)
    result = followChecks(follower, followee)

    if result == True:
        follower.unfollow(followee)
        db.session.commit()
        return {"following": False}
    return result

@app.route("/<authorid>/clips")
def getClipIdsForAuthor(authorid):
    clips = Clip.query.order_by(Clip.dateOfCreation.desc()).filter_by(authorId=authorid).all()
    clipIds = []

    for clip in clips:
        clipIds.append(clip.id)

    return jsonify(clipIds)

@app.route("/clips/info/<clipid>")
def getClipInformation(clipid):
    clip = Clip.query.get_or_404(clipid)

    return {"title": clip.title, "description": clip.description, "author": clip.author.username, "date": str(clip.dateOfCreation), "authorId": clip.author.id}

@app.route("/follow/clips/<userid>")
def getFollowFeed(userid):
    clipIds = []
    user = User.query.get(userid)
    if user is None:
        return errorMessageWithCode("User does not exist", 404)

    followedClips = user.followedClips()
    for clip in followedClips:
        clipIds.append(clip.id)

    return jsonify(clipIds)

