import mysql.connector


db = mysql.connector.connect(
    host="localhost",
    user="leo",
    password="bourrel",
    database="adenoa"
)
cursor = db.cursor()
