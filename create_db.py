import mysql.connector

# connection to DB
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="users"
)

my_cursor = mydb.cursor()
# create database in mysql
my_cursor.execute("CREATE DATABASE users")

# my_cursor.execute("SHOW DATABASES")
# for db in my_cursor:
#    print(db)
my_cursor.execute("CREATE TABLE acounts (name VARCHAR(255),email VARCHAR(255), password VARCHAR(255), user_id cINTEGER AUTO_INCREMENT PRIMARY Key"))
my_cursor.execute("SHOW TABLES")
#for table in my_cursor:
#    print(table)     # table[0] to get another formatt (without parantesis)
#sqlStuff = "INSERT INFO users (name, email, age) VALUES (%s, %s, %s)"
#record1 = ("John" , "john@codemy.com", 40)