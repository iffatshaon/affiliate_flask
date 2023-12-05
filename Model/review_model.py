from Utils.database import cursor, connection
from flask import make_response, send_file

class review_model:
    def __init__(self):
        self.con = connection
        self.cur = cursor
    
    def getall_model(self):
        return make_response({"result":"Incomplete API"})

    def update_model(self,data):
        return make_response({"result":"Incomplete API"})
    
    def create_model(self,data):
        return make_response({"result":"Incomplete API"})