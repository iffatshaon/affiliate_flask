from flask import Blueprint, request
from Model.captcha_model import captcha_model

model = captcha_model()

captcha = Blueprint("captcha_blueprint",__name__)

@captcha.route("/new")
def new():
    return model.new_model()

@captcha.route("/match", methods=['POST'])
def match():
    return model.match_model(request.json())