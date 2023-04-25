from flask import Flask, redirect, render_template, request, url_for, jsonify
import sqlite3
from flask_bootstrap import Bootstrap
import datetime
from server.felica import readIDm, ReadIDm

DATABASE = 'server/database.db'

app = Flask(__name__)
bootstrap = Bootstrap(app)
thread_readIDm = ReadIDm(3)
thread_readIDm.setDaemon(True)
thread_readIDm.start()

@app.route('/')
async def index():
    con = sqlite3.connect(DATABASE)
    con.row_factory = sqlite3.Row 
    cur = con.cursor()
    db_users = cur.execute('SELECT logs.idm, name, grade, class, atdNum, status, datetime FROM logs JOIN users ON logs.idm = users.idm JOIN ( SELECT idm, MAX(id) AS latestId FROM logs GROUP BY idm ) latestLogs ON logs.idm = latestLogs.idm AND logs.id = latestLogs.latestId').fetchall()
    con.close()
    return render_template(
        'index.html',
        persons=db_users
    )

@app.route('/userStatus')
async def userStatus():
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    db_users = cur.execute('SELECT logs.idm, status, datetime FROM logs JOIN users ON logs.idm = users.idm JOIN ( SELECT idm, MAX(id) AS latestId FROM logs GROUP BY idm ) latestLogs ON logs.idm = latestLogs.idm AND logs.id = latestLogs.latestId').fetchall()
    con.close()
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

@app.route('/checkin', methods=['POST'])
async def handle():
    _idm = request.form['idm']
    nowdate = datetime.datetime.now()
    parsedDate = f'{nowdate.year}年{nowdate.month}月{nowdate.day}日{nowdate.hour}時{nowdate.minute}分{nowdate.second}秒'
    try:
        con = sqlite3.connect(DATABASE)
        _status = not con.execute(f'SELECT status FROM logs JOIN ( SELECT idm, MAX(id) AS latestId FROM logs GROUP BY idm ) latestLogs ON logs.idm = latestLogs.idm AND logs.id = latestLogs.latestId WHERE logs.idm = "{_idm}"').fetchone()[0]
        con.execute(f'INSERT INTO logs(datetime, idm, status) VALUES("{parsedDate}", "{_idm}", {_status})')
        con.commit()
        con.close()
    except AttributeError:
        pass

    return redirect(url_for('index'))

@app.route('/name')
async def name():

    return render_template(
        'name.html'
    )

@app.route('/user_register', methods=['POST', 'GET'])
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
        con = sqlite3.connect(DATABASE)
        con.execute(f'INSERT INTO users(idm, name, grade, class, atdNum) VALUES("{_idm}", "{_name}", {_grade}, {_class}, {_atdNum})')
        nowdate = datetime.datetime.now()
        parsedDate = f'{nowdate.year}年{nowdate.month}月{nowdate.day}日{nowdate.hour}時{nowdate.minute}分{nowdate.second}秒'
        con.execute(f'INSERT INTO logs(datetime, idm, status) VALUES("{parsedDate}", "{_idm}", 0)')
        con.commit()
        con.close()
    except AttributeError:
        pass

    return redirect(url_for('index'))

