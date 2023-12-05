from Utils.database import cursor,connection
from flask import make_response, send_file

class price_model:
    def __init__(self):
        self.con = connection
        self.cur = cursor
    
    def getall_model(self):
        self.con.reconnect()
        self.cur.execute(f"SELECT * FROM price")
        result = self.cur.fetchall()
        return make_response({"result":result})

    def update_model(self,data):
        self.con.reconnect()
        try:
            self.cur.execute(f"UPDATE price plan='{data['plan']}', description='{data['description']}', price='{data['price']}' WHERE id='{data['id']}' ")
            return make_response({"result":data},201)
        except:
            return make_response({"result":"Unable to Update"},204)
    
    def add_model(self,data):
        self.con.reconnect()
        try:
            self.cur.execute(f"INSERT INTO price(plan,description,price) VALUES('{data['plan']}','{data['description']}','{data['price']}')")
            return make_response({"result":data},201)
        except:
            return make_response({"result":"Unable to Add"},204)