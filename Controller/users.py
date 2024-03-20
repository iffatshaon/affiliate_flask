from flask import Blueprint, request
from Model.users_model import users_model

model = users_model()

users = Blueprint("users_blueprint",__name__)

@users.route("/register",methods=["POST"])
def register():
    return model.register_model(request.get_json())

@users.route("/login", methods=["POST"])
def login():
    return model.login_model(request.get_json())

@users.route("/")
def allusers():
    return model.getusers_model()

@users.route("/me")
def personal():
    return model.get_personal_model(request.headers.get('Authorization'))

@users.route("/token")
def tokens():
    return model.remainingtoken_model(request.headers.get('Authorization'))

@users.route("/<id>/renew", methods=["PUT"])
def renew(id):
    return model.renew_token(id, request.get_json())

@users.route("/confirm/<hash>")
def confirmuser(hash):
    return model.confirmuser_model(hash)

@users.route("/<id>", methods=["GET"])
def getSingleUSer(id):
    return model.get_single_user_model(id, request.headers.get('Authorization'))

@users.route("/<id>", methods=["PUT"])
def updateUser(id):
    return model.updateUser_model(request.get_json(), id, request.headers.get('Authorization'))

@users.route("/<id>", methods=["DELETE"])
def deleteUser(id):
    return model.delete_model(id, request.headers.get("Authorization"))