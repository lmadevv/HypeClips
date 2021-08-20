from flask import Flask
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
    return None

@app.route('/register', methods=['POST'])
def register():
    return None

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