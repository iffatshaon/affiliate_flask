from Utils.database import cursor,connection
from flask import make_response, send_file
import mysql.connector

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
        # Generate column names and placeholders
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO price ({columns}) VALUES ({placeholders})"
        try:
            # Execute the query using the values from `data`
            self.cur.execute(query, tuple(data.values()))
            self.con.commit()  # Make sure to commit the changes
            return make_response({"result": data}, 201)
        except mysql.connector.Error as err:
            print("Error:", err)
            return make_response({"result": "Unable to Add"}, 204)