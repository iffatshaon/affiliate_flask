from Utils.database import cursor,connection
from flask import make_response
from Model.captcha_model import captcha_model
import bcrypt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import string
from bs4 import BeautifulSoup
import os

captcha = captcha_model()

def generate_random_string(length=16):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

def send_email(receiver_email, subject, message):
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_username = os.getenv("SMTP_MAIL")
    smtp_password = os.getenv("SMTP_PASSWORD")

    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = receiver_email
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'html'))

    s = smtplib.SMTP_SSL(smtp_server, port=smtp_port)
    s.login(smtp_username, smtp_password)
    s.sendmail(smtp_username, receiver_email, msg.as_string())
    s.quit()

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
            self.cur.execute(f"SELECT * FROM users where email='{data['email']}' OR mobile='{data['mobile']}'")
            res = self.cur.fetchall()
            confirm_hash = generate_random_string()
            if(len(res)>0):
                return make_response({"result":"Email and/or Mobile number has already been used"},409)
            else:
                try:
                    self.cur.execute(f"INSERT INTO users(name,mobile,username,email,password,confirm) VALUES('{data['name']}','{data['mobile']}','{data['username']}','{data['email']}','{password}','{confirm_hash}')")
                    subject = "Welcome to Faisalitab AI"
                    with open("./Utils/activation.html", "r") as file:
                        message = file.read()
                    soup = BeautifulSoup(message,"html.parser")
                    a_tag = soup.find('a')
                    a_tag["href"]="http://127.0.0.1:5000/user/confirm/"+confirm_hash
                    send_email(data["email"], subject, str(soup))
                    return make_response({"result":"Verification link sent to mail"},201)
                except:
                    return make_response({"result":"Unable to Register"},204)
        else:
            return make_response({"result":"Invalid captcha"},204)
    
    def confirmuser_model(self,data):
        self.con.reconnect()
        self.cur.execute(f"UPDATE users set confirm='1' where confirm='{data}'")
        return make_response({"result":"Registration successful"},201)

    def getusers_model(self):
        self.con.reconnect()
        self.cur.execute("SELECT * FROM users")
        result = self.cur.fetchall()
        if len(result)>0:
            return make_response({"result":result})
        else:
            return make_response({"result":"No data"},204)
    
    def remainingtoken_model(self,data):
        self.con.reconnect()
        self.cur.execute("SELECT token FROM users where id=%s",[data["auth"]])
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
                if result[0]['confirm']!=1:
                    return make_response({"result":False, "reason":"Verify user","email":result[0]["email"]})
                return make_response({"result":True, "name":result[0]['name'],"email":result[0]["email"]})
            else:
                return make_response({"result":False,"reason":"User not found"})
        else:
            return make_response({"result":"Invalid captcha"})
        