from flask import Flask, redirect, render_template, request, url_for, jsonify
import sqlite3
from felica.app import readIDm
from flask_bootstrap import Bootstrap
import requests
import datetime

DATABASE = 'server/database.db'

app = Flask(__name__)
bootstrap = Bootstrap(app)


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
        
    requests.get("http://localhost:5000/felica/stop")
    _idm = readIDm()
    requests.get("http://localhost:5000/felica/start")

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
