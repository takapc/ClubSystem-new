from flask import Flask, redirect, render_template, request, url_for, jsonify
import sqlite3
from flask_bootstrap import Bootstrap
import time
import random
from server.felica import readIDm, ReadIDm

DATABASE = 'server/database.db'

app = Flask(__name__)
bootstrap = Bootstrap(app)
thread_readIDm = ReadIDm(3)
thread_readIDm.setDaemon(True)
thread_readIDm.start()

@app.route('/')
async def index():
    with sqlite3.connect(DATABASE) as con:
        con.row_factory = sqlite3.Row 
        cur = con.cursor()
        db_users = cur.execute('SELECT logs.idm, name, grade, class, atdNum, status, strftime("%Y年%m月%d日 %H時%M分%S秒", datetime("datetime", "+9 hours")) as datetime FROM logs JOIN users ON logs.idm = users.idm JOIN ( SELECT idm, MAX(id) AS latestId FROM logs GROUP BY idm ) latestLogs ON logs.idm = latestLogs.idm AND logs.id = latestLogs.latestId').fetchall()
    return render_template(
        'index.html',
        persons=db_users
    )

@app.route('/userStatus')
async def userStatus():
    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        db_users = cur.execute('SELECT logs.idm, status, strftime("%Y年%m月%d日 %H時%M分%S秒", datetime(datetime, "+9 hours")) as datetime FROM logs JOIN users ON logs.idm = users.idm JOIN ( SELECT idm, MAX(id) AS latestId FROM logs GROUP BY idm ) latestLogs ON logs.idm = latestLogs.idm AND logs.id = latestLogs.latestId').fetchall()
    return jsonify(db_users)

@app.route('/isReadActive')
def isReadActive():
    return jsonify({'isReadActive': thread_readIDm.alive})

@app.route('/readActivate')
def readActivate():
    thread_readIDm.begin()
    return jsonify({'isReadActive': thread_readIDm.alive})

@app.route('/readDeactivate')
def readDeactivate():
    thread_readIDm.stop()
    return jsonify({'isReadActive': thread_readIDm.alive})

@app.route('/checkin/<_idm>', methods=['GET'])
async def handle(_idm):
    try:
        with sqlite3.connect(DATABASE) as con:
            if time.time() - float(con.execute('SELECT strftime("%s", datetime) as unixtime FROM logs JOIN ( SELECT idm, MAX(id) AS latestId FROM logs GROUP BY idm ) latestLogs ON logs.idm = latestLogs.idm AND logs.id = latestLogs.latestId WHERE logs.idm = ?', (_idm,)).fetchone()[0]) > 60:
                _status = not con.execute(f'SELECT status FROM logs JOIN ( SELECT idm, MAX(id) AS latestId FROM logs GROUP BY idm ) latestLogs ON logs.idm = latestLogs.idm AND logs.id = latestLogs.latestId WHERE logs.idm = ?', (_idm,)).fetchone()[0]
                con.execute('INSERT INTO logs(datetime, idm, status) VALUES(datetime("now"), ?, ?)', (_idm, _status))
                con.commit()
    except AttributeError:
        pass

    return redirect(url_for('userStatus'))

@app.route('/name')
async def name():

    return render_template(
        'name.html'
    )

@app.route('/user_register', methods=['POST'])
async def user_register():
    _name = request.form['name']
    _grade = request.form['grade']
    _class = request.form['class']
    _atdNum = request.form['atdNum']
    
    if thread_readIDm.alive:
        thread_readIDm.stop()
        _idm = readIDm()
        thread_readIDm.begin()
    else:
        _idm = readIDm()

    try:
        with sqlite3.connect(DATABASE) as con:
            con.execute(f'INSERT INTO users(idm, name, grade, class, atdNum) VALUES("{_idm}", "{_name}", {_grade}, {_class}, {_atdNum})')
            con.execute(f'INSERT INTO logs(datetime, idm, status) VALUES(datetime("now"), ?, 0)', (_idm,))
            con.commit()
    except AttributeError:
        pass

    return redirect(url_for('index'))

@app.route('/user_register_no_card', methods=['POST'])
async def user_register_no_card():
    _name = request.form['name']
    _grade = request.form['grade']
    _class = request.form['class']
    _atdNum = request.form['atdNum']
    _noCard = request.form['noCard']

    _idm = format(random.randrange(2**62, 2**64-1, 1), '016x')

    try:
        with sqlite3.connect(DATABASE) as con:
            con.execute(f'INSERT INTO users(idm, name, grade, class, atdNum) VALUES("{_idm}", "{_name}", {_grade}, {_class}, {_atdNum})')
            con.execute(f'INSERT INTO logs(datetime, idm, status) VALUES(datetime("now"), ?, 0)', (_idm,))
            con.commit()
    except AttributeError:
        pass

    return redirect(url_for('index'))
