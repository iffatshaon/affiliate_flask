import json
from Utils.database import cursor

class user_model():
    def __init__(self):
        self.cur = cursor
        
    def register_model(self,data):
        self.cur.execute(f"INSERT INTO users(firstName,lastName,username,email,password) VALUES('{data['firstName']}','{data['lastName']}','{data['userName']}','{data['email']}','{data['password']}')")
        return "Registering user"
    
    def getusers_model(self):
        self.cur.execute("SELECT * FROM users")
        result = self.cur.fetchall()
        return json.dumps(result)
    
    def updateUser_model(self,data):
        sql = "UPDATE users SET"
        for x in data:
            if x != "id":
                sql+=f" {x}='{data[x]}',"
        sql = sql[:-1]
        sql += f" WHERE id={data['id']}"
        self.cur.execute(sql)
        if self.cur.rowcount>0:
            return "Updated User"
        else:
            return "Nothing to update"