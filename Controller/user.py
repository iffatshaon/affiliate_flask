from flask import Blueprint, request
from Model.user_model import user_model

model = user_model()

user = Blueprint("user_blueprint",__name__)

@user.route("/register",methods=["POST"])
def register():
    return model.register_model(request.get_json())

@user.route("/login", methods=["POST"])
def login():
    return model.login_model(request.get_json())

@user.route("/all")
def users():
    return model.getusers_model()

@user.route("/update", methods=["PUT"])
def updateUser():
    return model.updateUser_model(request.get_json())