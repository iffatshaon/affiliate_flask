import json
from Utils.database import cursor
from flask import make_response

class user_model():
    def __init__(self):
        self.cur = cursor
        
    def register_model(self,data):
        try:
            self.cur.execute(f"INSERT INTO users(firstName,lastName,username,email,password) VALUES('{data['firstName']}','{data['lastName']}','{data['userName']}','{data['email']}','{data['password']}')")
            return make_response({"result":data},201)
        except:
            return make_response({"result":"Unable to Register"},204)
    
    def getusers_model(self):
        self.cur.execute("SELECT * FROM users")
        result = self.cur.fetchall()
        if len(result)>0:
            return make_response({"result":result})
        else:
            return make_response({"result":"No data"},204)

    
    def updateUser_model(self,data):
        sql = "UPDATE users SET"
        for x in data:
            if x != "id":
                sql+=f" {x}='{data[x]}',"
        sql = sql[:-1]
        sql += f" WHERE id={data['id']}"
        self.cur.execute(sql)
        if self.cur.rowcount>0:
            return make_response({"result":data},201)
        else:
            return make_response({"result":"Nothing to update"},204)