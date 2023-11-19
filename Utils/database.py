import mysql.connector
import os

cursor = ''
try:
    con = mysql.connector.connect(host=os.getenv("SQL_HOST"),username=os.getenv("SQL_USERNAME"), password=os.getenv("SQL_PASSWORD"),database=os.getenv("SQL_DATABASE"),autocommit=True)
    cursor = con.cursor(dictionary=True)
    print("connection to database successful")
except:
    print("Error conencting")