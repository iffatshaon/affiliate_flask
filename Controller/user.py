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

@user.route("/token")
def tokens():
    return model.remainingtoken_model(request.headers.get('Authorization'))

@user.route("/renew", methods=["POST"])
def renew():
    return model.renew_token(request.get_json())

@user.route("/confirm/<hash>")
def confirmuser(hash):
    return model.confirmuser_model(hash)

@user.route("/update", methods=["PUT"])
def updateUser():
    return model.updateUser_model(request.get_json(),request.headers.get('Authorization'))