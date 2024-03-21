import jwt
from flask import make_response
import os

def checkToken(token):
        if not token:
            return make_response({"result": "Token not found"}, 401)
        try:
            token = token.split()[1]
            print("Token ",token)
            decode = jwt.decode(token,str(os.getenv("SECRET_KEY")),"HS256")
            return decode['id']
        except:
            return make_response({"result": "Token expired"}, 401)

def checkAdmin(id):
    if(id==0):
         return True
    else:
         return False