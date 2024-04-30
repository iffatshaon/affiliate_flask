from flask import Blueprint, request
from Model.sites_model import sites_model

model = sites_model()

sites = Blueprint("sites_blueprint",__name__)

@sites.route("", methods=["GET"])
def get():
    type = request.args.get('type')
    return model.getall_model(type, request.headers.get('Authorization'))

# @sites.route("/<user>")
# def getuser(user):
#     return model.getuser_model(user, request.headers.get('Authorization'))

@sites.route("", methods=["PUT"])
def update():
    type = request.args.get('type')
    return model.update_model(request.get_json(),request.headers.get('Authorization'))

@sites.route("", methods=["POST"])
def add():
    type = request.args.get('type')
    return model.add_model(request.get_json(),request.headers.get('Authorization'))

@sites.route("", methods=["DELETE"])
def delete():
    type = request.args.get('type')
    return model.delete_model(request.get_json(),request.headers.get('Authorization'))

@sites.route("/publish", methods=["POST"])
def publish():
    return model.publish_model(request.get_json(),request.headers.get('Authorization'))

@sites.route("/category", methods=["POST"])
def get_category():
    return model.get_category(request.get_json(), request.headers.get('Authorization'))
