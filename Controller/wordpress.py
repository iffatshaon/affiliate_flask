from flask import Blueprint, request
from Model.wordpress_model import wordpress_model

model = wordpress_model()

wordpress = Blueprint("wordpress_blueprint",__name__)

@wordpress.route("/get")
def get():
    return model.getall_model()

@wordpress.route("/update", methods=["POST"])
def update():
    return model.update_model(request.get_json())

@wordpress.route("/add", methods=["POST"])
def add():
    return model.add_model(request.get_json())

@wordpress.route("/delete", methods=["POST"])
def delete():
    return model.delete_model(request.get_json())

@wordpress.route("/publish", methods=["POST"])
def publish():
    return model.publish_model(request.get_json())
