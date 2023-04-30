import sqlite3

DATABASE='server/database.db'

# idm name grade class atdNum
def create_users():
    con = sqlite3.connect(DATABASE)
    con.execute("create table if not exists users (idm TEXT primary key not null, name TEXT not null, grade INTEGER not null, class INTEGER not null, atdNum INTEGER not null)")
    con.close()

# id datetime idm status #datetime is UTC
def create_logs():
    con = sqlite3.connect(DATABASE)
    con.execute("create table if not exists logs (id INTEGER primary key autoincrement, datetime TEXT not null, idm TEXT not null, status BOOLEAN not null)")
    con.close()