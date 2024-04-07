from flask import Blueprint, request
from Model.sites_model import sites_model

model = sites_model()

sites = Blueprint("sites_blueprint",__name__)

@sites.route("/<site>", methods=["GET"])
def get(site):
    return model.getall_model(site, request.headers.get('Authorization'))

# @sites.route("/<user>")
# def getuser(user):
#     return model.getuser_model(user, request.headers.get('Authorization'))

@sites.route("/wordpress", methods=["PUT"])
def update():
    return model.update_model(request.get_json(),request.headers.get('Authorization'))

@sites.route("/wordpress", methods=["POST"])
def add():
    return model.add_model(request.get_json(),request.headers.get('Authorization'))

@sites.route("/wordpress", methods=["DELETE"])
def delete():
    return model.delete_model(request.get_json(),request.headers.get('Authorization'))

@sites.route("/publish", methods=["POST"])
def publish():
    return model.publish_model(request.get_json(),request.headers.get('Authorization'))
