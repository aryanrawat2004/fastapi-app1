import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',  # replace with your MySQL server
            user='root',  # replace with your MySQL username
            password='root',  # replace with your MySQL password
            database='Login'  # replace with your database name
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            return connection
    except Error as e:
        print(f"Error: {e}")
        return None
