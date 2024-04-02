from flask import Blueprint, request
from Model.articles_model import articles_model

model = articles_model()

articles = Blueprint("articles_blueprint",__name__)

@articles.route("", methods=["POST"])
def create():
    return model.create_model(request.get_json(), request.headers.get("Authorization"))

@articles.route("/createfree", methods=["POST"])
def createfree():
    return model.free_model(request.get_json())

@articles.route("/suggestion", methods=["POST"])
def suggestion():
    return model.suggestion_model(request.get_json(), request.headers.get("Authorization"))

@articles.route("", methods=["GET"])
def get_list():
    return model.get_list_model(request.headers.get("Authorization"))

@articles.route("/keyword", methods=["POST"])
def keyword():
    return model.keyword_model(request.get_json())

@articles.route("/<id>", methods=["GET"])
def edit(id):
    return model.edit_model(id, request.headers.get("Authorization"))

@articles.route("/<id>", methods=["PUT"])
def save(id):
    return model.save_model(id, request.get_json(), request.headers.get("Authorization"))