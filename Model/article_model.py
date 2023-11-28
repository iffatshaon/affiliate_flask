from Utils.database import cursor
from flask import make_response, send_file

class article_model:
    def __init__(self):
        self.cur = cursor
    
    def generate_cookie():
        return "cookie text"

    def create_model(self):
        cookie = self.generate_cookie()
        return make_response({"result":"Incomplete API"}) #send_file("text_file_path",mimetype="txt")
    
    def free_model(self,data):
        return make_response({"result":"Incomplete API"}) #send_file("text_file_path",mimetype="txt")
    
    def suggestion(self,data):
        return make_response({"result":"Incomplete API"}) #send_file("text_file_path",mimetype="txt")