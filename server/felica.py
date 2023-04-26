import nfc
import binascii
import threading
import time
import datetime
import sqlite3

DATABASE = 'server/database.db'

def readIDm():
    clf = nfc.ContactlessFrontend("usb")
    try:
        tag = clf.connect(rdwr={"targets": ["212F", "424F"], "on-connect": lambda tag: False})
    finally:
        clf.close()

    if tag.TYPE == "Type3Tag":
        idm = binascii.hexlify(tag.idm).decode()
    
    if idm:
        return idm
    else:
        raise AttributeError("cannot read IDm from this card.")
    
class ReadIDm(threading.Thread):
    def __init__(self, sleep):
        super(ReadIDm, self).__init__()
        self.alive = False
        self.sleep = sleep

    def begin(self):
        self.alive = True

    def stop(self):
        self.alive = False

    def run(self):
        while True:
            if self.alive:
                time.sleep(self.sleep)
                _idm = readIDm()
                nowdate = datetime.datetime.now()
                parsedDate = f'{nowdate.year}年{nowdate.month}月{nowdate.day}日{nowdate.hour}時{nowdate.minute}分{nowdate.second}秒'
                try:
                    con = sqlite3.connect(DATABASE)
                    if con.execute(f'select * from users where idm = "{_idm}"').fetchone() is None:
                        raise AttributeError("This user is not registered.")
                    if con.execute(f'select * from logs where idm = "{_idm}"').fetchone() is None:
                        _status = 1
                    else:
                        _status = not con.execute(f'SELECT status FROM logs JOIN ( SELECT idm, MAX(id) AS latestId FROM logs GROUP BY idm ) latestLogs ON logs.idm = latestLogs.idm AND logs.id = latestLogs.latestId WHERE logs.idm = "{_idm}"').fetchone()[0]
                    con.execute(f'INSERT INTO logs(datetime, idm, status) VALUES("{parsedDate}", "{_idm}", {_status})')
                    con.commit()
                    con.close()
                except AttributeError:
                    pass
                