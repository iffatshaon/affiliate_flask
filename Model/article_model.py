from Utils.database import cursor, connection
from flask import make_response, send_file

class article_model:
    def __init__(self):
        self.con = connection
        self.cur = cursor
    
    def generate_cookie():
        return "cookie text"

    def create_model(self):
        self.con.reconnect()
        cookie = self.generate_cookie()
        return make_response({"result":"Incomplete API"}) #send_file("text_file_path",mimetype="txt")
    
    def free_model(self,data):
        self.con.reconnect()
        return make_response({"result":"Incomplete API"}) #send_file("text_file_path",mimetype="txt")
    
    def suggestion_model(self,data):
        self.con.reconnect()
        return make_response({"result":"Incomplete API"}) #send_file("text_file_path",mimetype="txt")