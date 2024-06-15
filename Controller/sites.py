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

@sites.route("/<id>", methods=["PUT"])
def update(id):
    return model.update_model(id,request.get_json(),request.headers.get('Authorization'))

@sites.route("", methods=["POST"])
def add():
    return model.add_model(request.get_json(),request.headers.get('Authorization'))

@sites.route("/<id>", methods=["DELETE"])
def delete(id):
    return model.delete_model(id,request.headers.get('Authorization'))

@sites.route("/<site_id>/publish", methods=["POST"])
def publish(site_id):
    return model.publish_model(site_id, request.get_json(),request.headers.get('Authorization'))

@sites.route("/<site_id>/categories", methods=["POST"])
def get_category(site_id):
    return model.get_category(site_id, request.get_json(), request.headers.get('Authorization'))
