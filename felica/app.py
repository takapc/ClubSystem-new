import nfc
import binascii
import requests
import time

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
    
def readLoop():
    while True:
        try:
            idm = readIDm()
        except AttributeError:
            # 読み取れなかったことを通知するためエンドポイントを作る
            pass
            break
        res = requests.post("http://localhost:5000/checkin", data={"idm": idm})