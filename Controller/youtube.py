from flask import Blueprint, request
from Model.youtube_model import youtube_model

model = youtube_model()

youtube = Blueprint("youtube_blueprint",__name__)

@youtube.route("/get")
def getall():
    return model.getall_model()

@youtube.route("/get/<id>")
def getVideo(id):
    return model.get_model(id)

@youtube.route("/set", methods=["POST"])
def setVideo():
    return model.set_model(request.get_json())

@youtube.route("/add", methods=["POST"])
def add():
    return model.add_model(request.get_json())
