from Utils.database import cursor,connection
from flask import make_response, send_file

class youtube_model:
    def __init__(self):
        self.con = connection
        self.cur = cursor
    
    def getall_model(self):
        self.con.reconnect()
        self.cur.execute(f"SELECT * FROM videos")
        result = self.cur.fetchall()
        print(result)
        return make_response({"result":result})
    
    def get_model(self,vid):
        self.con.reconnect()
        self.cur.execute(f"SELECT url FROM videos WHERE id={vid}")
        result = self.cur.fetchall()
        return make_response({"result":result})

    def set_model(self,data):
        self.con.reconnect()
        self.cur.execute(f"UPDATE videos SET url='{data['url']}' WHERE id={data['id']}")
        return make_response({"result":data},201)
    
    def add_model(self,data):
        self.con.reconnect()
        try:
            self.cur.execute(f"INSERT INTO videos(url) VALUES('{data['url']}')")
            return make_response({"result":data},201)
        except:
            return make_response({"result":"Unable to Add"},204)