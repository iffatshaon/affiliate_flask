from flask import Blueprint, request
from Model.article_model import article_model

model = article_model()

article = Blueprint("article_blueprint",__name__)

@article.route("/create", methods=["POST"])
def create():
    return model.create_model(request.get_json())

@article.route("/create-free", methods=["POST"])
def createfree():
    return model.free_model(request.get_json())

@article.route("/suggestion", methods=["POST"])
def suggestion():
    return model.suggestion_model(request.get_json())