# How to run the server (testing):
# export FLASK_APP=application.py
# export FLASK_ENV=development
# flask run

# TESTING ACCOUNT DATABASE: USERNAME = bob PASSWORD = pass123

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(40), nullable=False)

@app.route('/login', methods=['POST'])
def login():
    users = User.query.all()

    for user in users:
        if (request.json['username'] == user.username):
            if (request.json['password'] == user.password):
                return {"status": "successful login"}, 200

    return {"status": "not a valid login"}, 401

@app.route('/register', methods=['POST'])
def register():
    users = User.query.all()

    for user in users:
        if (request.json['username'] == user.username):
            return {"status": "unsuccessful registration"}, 400

    if (len(request.json['username']) > 20) or (len(request.json['password']) > 40):
        return {"status": "unsuccessful registration"}, 400

    newUser = User(username=request.json['username'], password=request.json['password'])
    db.session.add(newUser)
    db.session.commit()

    return {"status": "successful registration"}, 200

@app.route('/clips')
def getClips():
    return None

@app.route('/clips', methods=['PUT'])
def addClips():
    return None

@app.route('/clips/<clipid>')
def getClip():
    return None

@app.route('/clips', methods=['DELETE'])
def deleteClip():
    return None

@app.route('/comments/<clipid>')
def getComments():
    return None

@app.route('/comments/<clipid>', methods=['PUT'])
def addComment():
    return None

@app.route('/user/<userid>')
def getUser():
    return None

@app.route('/follow/<follower>/<followee>')
def isFollowing():
    return None

@app.route('/follow/<follower>/<followee>', methods=['PUT'])
def follow():
    return None

@app.route('/follow/<follower>/<followee>', methods=['DELETE'])
def unfollow():
    return None