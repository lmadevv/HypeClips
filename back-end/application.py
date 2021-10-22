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

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(40), nullable=False)
    clips = db.relationship("Clip", backref="user", lazy=True)

class Clip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    clipUuid = db.Column(db.String(100), nullable=False)
    authorId = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    dateOfCreation = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    @staticmethod
    def getClipPath(uuid):
        return os.path.join(os.path.join(os.getcwd(), "clips"), f"{uuid}.mp4")

def errorMessageWithCode(status, code):
    return {"status": status}, code

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
    clips = Clip.query.all()

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

    newClip = Clip(clipUuid=clipUuid, authorId=int(request.form.get("authorId")))
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
def getComments():
    return None

@app.route("/comments/<clipid>", methods=["PUT"])
def addComment():
    return None

@app.route("/user/<userid>")
def getUser():
    return None

@app.route("/follow/<follower>/<followee>")
def isFollowing():
    return None

@app.route("/follow/<follower>/<followee>", methods=["PUT"])
def follow():
    return None

@app.route("/follow/<follower>/<followee>", methods=["DELETE"])
def unfollow():
    return None

@app.route("/<authorid>/clips")
def getClipIdsForAuthor(authorid):
    clips = Clip.query.filter_by(authorId=authorid).all()
    clipIds = []

    for clip in clips:
        clipIds.append(clip.id)

    return jsonify(clipIds)