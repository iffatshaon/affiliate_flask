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
        if 'id' not in data:
            return make_response({"result": "Missing 'id'"}, 400)
        
        assignments = ', '.join([f"{key} = %s" for key in data if key != 'id'])
        data_values = tuple(data[key] for key in data if key != 'id')
        conditions = (data['id'],)
        sql_query = f"UPDATE price SET {assignments} WHERE id = %s"
        try:
            self.cur.execute(sql_query, data_values + conditions)
            self.con.commit()
            return make_response({"result": data}, 201)
        except mysql.connector.Error as err:
            print("Error:", err)
            return make_response({"result": "Unable to Update"}, 204)
    
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
    
    def delete_model(self,data):
        self.con.reconnect()
        query = f"DELETE FROM price WHERE id={data['id']}"
        try:
            # Execute the query using the values from `data`
            self.cur.execute(query)
            self.con.commit()  # Make sure to commit the changes
            return make_response({"result": data}, 201)
        except mysql.connector.Error as err:
            print("Error:", err)
            return make_response({"result": "Unable to Add"}, 204)
    
    def get_payment_model(self):
        self.con.reconnect()
        self.cur.execute(f"SELECT * FROM payment")
        result = self.cur.fetchall()
        return make_response({"result":result})
        
    def payment_model(self,data):
        self.con.reconnect()
        query = f"INSERT INTO payment(package_id,user_id,transaction_id,transaction_method) VALUES ('{data['package_id']}','{data['user_id']}','{data['transaction_id']}','{data['transaction_method']}')"
        try:
            # Execute the query using the values from `data`
            self.cur.execute(query)
            self.con.commit()  # Make sure to commit the changes
            return make_response({"result": data}, 201)
        except mysql.connector.Error as err:
            print("Error:", err)
            return make_response({"result": "Unable to Add"}, 204)
    
    def approve_model(self,data):
        self.con.reconnect()
        sql_query = f"UPDATE payment SET approved=1 WHERE id = {data['id']}"
        try:
            self.cur.execute(sql_query)
            self.con.commit()
            return make_response({"result": data}, 201)
        except mysql.connector.Error as err:
            print("Error:", err)
            return make_response({"result": "Unable to Update"}, 204)        

    def get_offers(self):
        self.con.reconnect()
        self.cur.execute(f"SELECT * FROM offer")
        result = self.cur.fetchall()
        return make_response({"offers":result})

    def add_offer(self, data):
        self.con.reconnect()
        query = f"INSERT INTO offer (offers) VALUES ('{data['offer']}')"
        try:
            self.cur.execute(query)
            self.con.commit()
            return make_response({"result": data})
        except Exception as err:
            return make_response({"result": "Error: "+str(err)}, 400)
    
    def get_coupons(self):
        self.con.reconnect()
        self.cur.execute(f"SELECT * FROM coupon")
        result = self.cur.fetchall()
        return make_response({"coupons":result})

    def get_coupon_price(self, data):
        self.cur.execute(f"SELECT * FROM coupon where code='{data['code']}'")
        result = self.cur.fetchall()
        if len(result)>0:
            discount = result[0]["discount"]
        else:
            return make_response({"Result":"Invalid code"},400)
        res={"discountDecimal":int(discount)/100}
        if 'package' in data:
            self.cur.execute(f"SELECT desc1 FROM price where id='{data['package']}'")
            result = self.cur.fetchall()
            if len(result)>0:
                res['price']=(int(result[0]['desc1'].split(" ")[0]))*(1-int(discount)/100)
            else:
                return make_response({"Result":"Invalid package"},400)
        return make_response(res)

    def add_coupon(self, data):
        self.con.reconnect()
        query = f"INSERT INTO coupon (code, discount) VALUES ('{data['code']}','{data['discount']}')"
        try:
            self.cur.execute(query)
            self.con.commit()
            return make_response({"result": data})
        except Exception as err:
            return make_response({"result": "Error: "+str(err)}, 400)