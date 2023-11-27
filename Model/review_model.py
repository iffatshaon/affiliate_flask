from Utils.database import cursor
from flask import make_response, send_file

class article_model:
    def __init__(self):
        self.cur = cursor
    
    def getall_model(self):
        return "cookie text"

    def update_model(self,data):
        return make_response(send_file("text_file_path",mimetype="txt"))
    
    def create_model(self,data):
        return make_response(send_file("text_file_path",mimetype="txt"))