from Utils.database import cursor
from flask import make_response, send_file

class article_model:
    def __init__(self):
        self.cur = cursor
    
    def getall_model(self):
        return make_response({"result":"Incomplete API"})
    
    def get_model(self,data):
        return make_response({"result":"Incomplete API"})

    def set_model(self,data):
        return make_response({"result":"Incomplete API"})
    
    def add_model(self,data):
        return make_response({"result":"Incomplete API"})