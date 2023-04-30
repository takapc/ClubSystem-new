import nfc
import binascii
import threading
import time
import sqlite3

DATABASE = 'server/database.db'

def readIDm():
    with nfc.ContactlessFrontend("usb") as clf:
        tag = clf.connect(rdwr={"targets": ["212F", "424F"], "on-connect": lambda tag: False})

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

    def readIDm(self):
        with nfc.ContactlessFrontend("usb") as clf:
            tag = clf.connect(rdwr={"targets": ["212F", "424F"], "on-connect": lambda tag: False}, terminate=lambda: not self.alive)

        if tag is None:
            raise AttributeError("cannot read IDm from this card.")

        if tag.TYPE == "Type3Tag":
            idm = binascii.hexlify(tag.idm).decode()
        
        if idm:
            return idm
        else:
            raise AttributeError("cannot read IDm from this card.")

    def run(self):
        while True:
            if self.alive:
                try:
                    _idm = self.readIDm()
                    with sqlite3.connect(DATABASE) as con:
                        if con.execute(f'select * from users where idm = "{_idm}"').fetchone() is None:
                            raise AttributeError("This user is not registered.")
                        if con.execute(f'select * from logs where idm = "{_idm}"').fetchone() is None:
                            _status = 1
                        else:
                            _status = not con.execute(f'SELECT status FROM logs JOIN ( SELECT idm, MAX(id) AS latestId FROM logs GROUP BY idm ) latestLogs ON logs.idm = latestLogs.idm AND logs.id = latestLogs.latestId WHERE logs.idm = "{_idm}"').fetchone()[0]
                        if time.time() - float(con.execute('SELECT strftime("%s", datetime) as unixtime FROM logs JOIN ( SELECT idm, MAX(id) AS latestId FROM logs GROUP BY idm ) latestLogs ON logs.idm = latestLogs.idm AND logs.id = latestLogs.latestId WHERE logs.idm = ?', (_idm,)).fetchone()[0]) > 60:
                            con.execute(f'INSERT INTO logs(datetime, idm, status) VALUES(datetime("now"), "{_idm}", {_status})')
                            con.commit()
                except AttributeError:
                    pass
                