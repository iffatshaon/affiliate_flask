from flask import Blueprint, request
from Model.article_model import article_model

model = article_model()

article = Blueprint("article_blueprint",__name__)

@article.route("/", methods=["POST"])
def create():
    return model.create_model(request.get_json(), request.headers.get("Authorization"))

@article.route("/createfree", methods=["POST"])
def createfree():
    return model.free_model(request.get_json())

@article.route("/suggestion", methods=["POST"])
def suggestion():
    return model.suggestion_model(request.get_json())

@article.route("/", methods=["GET"])
def get_list():
    return model.get_list_model(request.headers.get("Authorization"))

@article.route("/keyword", methods=["POST"])
def keyword():
    return model.keyword_model(request.get_json())

@article.route("/<id>", methods=["GET"])
def edit(id):
    return model.edit_model(id, request.headers.get("Authorization"))

@article.route("/<id>", methods=["PUT"])
def save(id):
    return model.save_model(id, request.get_json(), request.headers.get("Authorization"))