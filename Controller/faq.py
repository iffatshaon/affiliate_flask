from flask import Blueprint, request
from Model.faq_model import faq_model

model = faq_model()

faq = Blueprint("faq_blueprint",__name__)

@faq.route("/get")
def get():
    return model.getall_model()

@faq.route("/update", method=["POST"])
def update():
    return model.update_model(request.get_json())

@faq.route("/add", method=["POST"])
def add():
    return model.add_model(request.get_json())
