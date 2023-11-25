from flask import Blueprint, request
from Model.article_model import article_model

model = article_model()

article = Blueprint("captcha_blueprint",__name__)

@article.route("/create", method=["POST"])
def create():
    return model.create_model(request.get_json())

@article.route("/create-free", method=["POST"])
def createfree():
    return model.free_model(request.get_json())