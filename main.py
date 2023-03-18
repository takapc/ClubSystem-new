from flaskr import app
from flask import redirect, render_template, request, url_for
import sqlite3
import nfc
import binascii

DATABASE = 'database.db'

@app.route('/')
def index():
    con = sqlite3.connect(DATABASE)
    db_persons = con.execute('SELECT * FROM PERSONS').fetchall()
    con.close()
    persons = []
    for row in db_persons:
        persons.append({'idm': row[0], 'name': row[1], 'grade': row[2], 'class': row[3], 'number': row[4], 'status': row[5], 'id': row[6]})

    return render_template(
        'index.html',
        persons=persons
    )

@app.route('/handle')
def handle():
    try:
        clf = nfc.ContactlessFrontend('usb')
        tag = clf.connect(rdwr={'on-connect': lambda tag: False})
        idm = binascii.hexlify(tag.idm).decode('utf-8')
        clf.close()

        con = sqlite3.connect(DATABASE)
        con.execute('UPDATE PERSONS SET STATUS = STATUS * -1 WHERE IDM = "' + idm + '"')
        con.commit()
        con.close()
    except AttributeError:
        pass

    return redirect(url_for('index'))

@app.route('/name')
def name():

    return render_template(
        'name.html'
    )

@app.route('/user_register', methods=['POST', 'GET'])
def user_register():
    _name = request.form['name']
    _grade = request.form['grade']
    _class = request.form['class']
    _number = request.form['number']
    _id = request.form['id']

    try:
        clf = nfc.ContactlessFrontend('usb')
        tag = clf.connect(rdwr={'on-connect': lambda tag: False})
        _idm = binascii.hexlify(tag.idm).decode('utf-8')
        clf.close()

        con = sqlite3.connect(DATABASE)
        con.execute('INSERT INTO PERSONS VALUES(?, ?, ?, ?, ?, ?, ?)',
                 [_idm, _name, _grade, _class, _number, -1, _id])
        con.commit()
        con.close()
    except AttributeError:
        pass



    return redirect(url_for('index'))
