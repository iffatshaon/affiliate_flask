from flask import Blueprint, request
from Model.price_model import price_model

model = price_model()

price = Blueprint("price_blueprint",__name__)

@price.route("/get")
def get():
    return model.getall_model()

@price.route("/update", method=["POST"])
def update():
    return model.update_model(request.get_json())

@price.route("/add", method=["POST"])
def add():
    return model.add_model(request.get_json())
