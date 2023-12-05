from Utils.database import cursor, connection
from flask import make_response, send_file

class faq_model:
    def __init__(self):
        self.con = connection
        self.cur = cursor
    
    def getall_model(self):
        self.con.reconnect()
        self.cur.execute(f"SELECT * FROM faq")
        result = self.cur.fetchall()
        return make_response({"result":result})

    def update_model(self,data):
        self.con.reconnect()
        try:
            self.cur.execute(f"UPDATE faq question='{data['question']}', answer='{data['answer']}' WHERE id='{data['id']}' ")
            return make_response({"result":data},201)
        except:
            return make_response({"result":"Unable to Update"},204)
    
    def add_model(self,data):
        self.con.reconnect()
        try:
            self.cur.execute(f"INSERT INTO faq(question,answer) VALUES('{data['question']}','{data['answer']}')")
            return make_response({"result":data},201)
        except:
            return make_response({"result":"Unable to Add"},204)