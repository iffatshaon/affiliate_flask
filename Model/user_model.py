from Utils.database import cursor
from flask import make_response
from Model.captcha_model import captcha_model

captcha = captcha_model()

class user_model():
    def __init__(self):
        self.cur = cursor
        
    def encrypt(self,password):
        return "encrypted"

    def register_model(self,data):
        getMatch = captcha.match_model({"hash":data.hash,"text":data.text})
        if getMatch.result:
            password = self.encrypt(data.password)
            try:
                self.cur.execute(f"INSERT INTO users(firstName,lastName,username,email,password) VALUES('{data['firstName']}','{data['lastName']}','{data['userName']}','{data['email']}','{password}')")
                return make_response({"result":data},201)
            except:
                return make_response({"result":"Unable to Register"},204)
        else:
            return make_response({"result":"Invalid captcha"})
    
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
    
    def login_model(self,data):
        getMatch = captcha.match_model({"hash":data.hash,"text":data.text})
        if getMatch.result:
            self.cur.execute(f"SELECT password FROM users WHERE email='{data.email}'")
            result = self.cur.fetchall()
            if len(result)>0:
                passenc = self.encrypt(data.password)
                if passenc == result.password:
                    return make_response({"result":True})
                else:
                    return make_response({"result":"Unable to login"})
            else:
                return make_response({"result":"User not found"})
        else:
            return make_response({"result":"Invalid captcha"})
        