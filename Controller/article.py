from flask import Blueprint, request
from Model.article_model import article_model

model = article_model()

article = Blueprint("article_blueprint",__name__)

@article.route("/create", methods=["POST"])
def create():
    return model.create_model(request.get_json(), request.headers.get("Authorization"))

@article.route("/createfree", methods=["POST"])
def createfree():
    return model.free_model(request.get_json())

@article.route("/suggestion", methods=["POST"])
def suggestion():
    return model.suggestion_model(request.get_json())

@article.route("/list", methods=["GET"])
def get_list():
    return model.get_list_model(request.get_json())

@article.route("/keyword", methods=["POST"])
def keyword():
    return model.keyword_model(request.get_json())

@article.route("/edit", methods=["POST"])
def edit():
    return model.edit_model(request.get_json(), request.headers.get("Authorization"))

@article.route("/save", methods=["POST"])
def save():
    return model.save_model(request.get_json(), request.headers.get("Authorization"))