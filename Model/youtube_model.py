from Utils.database import cursor
from flask import make_response, send_file

class youtube_model:
    def __init__(self):
        self.cur = cursor
    
    def getall_model(self):
        self.cur.execute(f"SELECT * FROM videos")
        result = self.cur.fetchall()
        return make_response({"result":result})
    
    def get_model(self,vid):
        self.cur.execute(f"SELECT url FROM videos WHERE id={vid}")
        result = self.cur.fetchall()
        return make_response({"result":result})

    def set_model(self,data):
        self.cur.execute(f"UPDATE videos SET url='{data['url']}' WHERE id={data['id']}")
        return make_response({"result":data},201)
        # try:
        # except:
        #     return make_response({"result":"Unable to Update"},204)
    
    def add_model(self,data):
        try:
            self.cur.execute(f"INSERT INTO videos(url) VALUES('{data['url']}')")
            return make_response({"result":data},201)
        except:
            return make_response({"result":"Unable to Add"},204)