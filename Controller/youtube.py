from flask import Blueprint, request
from Model.youtube_model import youtube_model

model = youtube_model()

youtube = Blueprint("youtube_blueprint",__name__)

@youtube.route("/getall")
def getall():
    return model.getall_model()

@youtube.route("/get/<vid>")
def getVideo(vid):
    return model.get_model(int(vid))

@youtube.route("/get/")
def getFirstVideo():
    return model.get_model(1)

@youtube.route("/set", methods=["POST"])
def setVideo():
    return model.set_model(request.get_json())

@youtube.route("/add", methods=["POST"])
def add():
    return model.add_model(request.get_json())
