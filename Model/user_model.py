from Utils.database import cursor,connection
from flask import make_response
from Model.captcha_model import captcha_model
from datetime import datetime
import bcrypt

captcha = captcha_model()

class user_model():
    def __init__(self):
        self.con = connection
        self.cur = cursor
        
    def encrypt(self,password):
        # password = password.encode()
        # hashed = bcrypt.hashpw(password, bcrypt.gensalt(12))
        # return str(hashed.decode('utf-8'))
        return password

    def register_model(self,data):
        self.con.reconnect()
        # getMatch = captcha.match_model({"hash":data['hash'],"text":data['text']})
        getMatch = {'result':True}
        if getMatch['result']:
            password = self.encrypt(data['password'])
            print(password)
            try:
                self.cur.execute(f"INSERT INTO users(firstName,lastName,username,email,password) VALUES('{data['firstName']}','{data['lastName']}','{data['username']}','{data['email']}','{password}')")
                return make_response({"result":data},201)
            except:
                return make_response({"result":"Unable to Register"},204)
        else:
            return make_response({"result":"Invalid captcha"})
    
    def getusers_model(self):
        self.con.reconnect()
        self.cur.execute("SELECT * FROM users")
        result = self.cur.fetchall()
        if len(result)>0:
            return make_response({"result":result})
        else:
            return make_response({"result":"No data"},204)

    
    def updateUser_model(self,data):
        self.con.reconnect()
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
        self.con.reconnect()
        # getMatch = captcha.match_model({"hash":data['hash'],"text":data['text']})
        getMatch = {'result':True}
        if getMatch['result']:
            self.cur.execute(f"SELECT * FROM users WHERE username='{data['username']}' and password='{self.encrypt(data['password'])}'")
            result = self.cur.fetchall()
            if len(result)>0:
                return make_response({"result":True})
            else:
                return make_response({"result":False})
        else:
            return make_response({"result":"Invalid captcha"})
        