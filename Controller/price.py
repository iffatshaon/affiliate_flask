from flask import Blueprint, request, make_response
from Model.price_model import price_model

model = price_model()

price = Blueprint("price_blueprint",__name__)

@price.route("/get")
def get():
    return model.getall_model()

@price.route("/update", methods=["POST"])
def update():
    return model.update_model(request.get_json())

@price.route("/add", methods=["POST"])
def add():
    return model.add_model(request.get_json())

@price.route("/delete", methods=["POST"])
def delete():
    return model.delete_model(request.get_json())

@price.route("/get_payments")
def get_payment():
    return model.get_payment_model()

@price.route("/payment", methods=["POST"])
def payment():
    return model.payment_model(request.get_json())

@price.route("/approve", methods=["PUT"])
def approve():
    return model.approve_model(request.get_json())

@price.route("/approve_payment/<tx>/<password>")
def approve_tx(tx, password):
    if password == "abc123def":
        return model.approve_model({"transaction_id":tx})
    else:
        return make_response({},401)

@price.route("/offer", methods=["GET"])
def getOffers():
    return model.get_offers()

@price.route("/offer", methods=["POST"])
def addOffer():
    return model.add_offer(request.get_json())

@price.route("/coupon/all", methods=["GET"])
def getCoupons():
    return model.get_coupons()

@price.route("/coupon", methods=["GET"])
def getCouponPrice():
    return model.get_coupon_price(request.args)

@price.route("/coupon", methods=["POST"])
def addcoupon():
    return model.add_coupon(request.get_json())
