from flask import Blueprint, request
from Model.gpt_model import gpt_model

model = gpt_model()

gpt = Blueprint("gpt_blueprint",__name__)

@gpt.route("/", methods=["POST"])
def query():
    return model.query_model(request.get_json(), request.headers.get("Authorization"))
