from flask import Blueprint, request
from Model.review_model import review_model

model = review_model()

review = Blueprint("review_blueprint",__name__)

@review.route("/get")
def get():
    return model.getall_model()

@review.route("/update", method=["POST"])
def update():
    return model.update_model(request.get_json())

@review.route("/create", method=["POST"])
def create():
    return model.create_model(request.get_json())
