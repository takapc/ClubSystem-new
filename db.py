import sqlite3

DATABASE='database.db'

def create_data():
    con = sqlite3.connect(DATABASE)
    con.execute("CREATE TABLE IF NOT EXISTS data (idm TEXT, name TEXT , status INTEGER)")
    con.close()

def create_persons():
    con = sqlite3.connect(DATABASE)
    con.execute("CREATE TABLE IF NOT EXISTS PERSONS (idm TEXT, name TEXT, grade INTEGER, class INTEGER, num INTEGER, status INTEGER, ID TEXT)")
    con.close()