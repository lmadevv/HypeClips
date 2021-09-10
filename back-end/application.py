from flask import Flask, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import uuid, os

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

class Clip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vidUUID = db.Column(db.String(100), nullable=False)

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
def getClips():
    return None

@app.route("/clips", methods=["PUT"])
def addClips():
    if "file" not in request.files:
        return errorMessageWithCode("no file part added to the request", 400)
    file = request.files["file"]
    if file.filename.split(".")[1].lower() != "mp4":
        return errorMessageWithCode("the file had the wrong format", 400)

    clipsPath = os.path.join(os.getcwd(), "clips")
    if not os.path.exists(clipsPath):
        os.mkdir(clipsPath)

    vidUUID = str(uuid.uuid4())
    fileName = vidUUID + ".mp4"
    fullPath = os.path.join(clipsPath, fileName)
    request.files["file"].save(fullPath)

    newClip = Clip(vidUUID=vidUUID)
    db.session.add(newClip)
    db.session.commit()

    return {"id": newClip.id, "vidUUID": vidUUID, "fullVidPath": fullPath}

@app.route("/clips/<clipid>")
def getClip():
    return None

@app.route("/clips", methods=["DELETE"])
def deleteClip():
    return None

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
