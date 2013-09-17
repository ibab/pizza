# encoding: UTF-8

import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, jsonify
from contextlib import closing

from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
import gevent.queue

import re
import time
import json

DATABASE = './pizza.sqlite3'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)

app.config.from_envvar('PIZZA_SETTINGS', silent=True)

host, port='localhost', 5000

def cents_to_euros(cents):
    return '{},{:02d} €'.format(int(cents / 100), cents % 100)

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/')
def show_entries():
    cur = g.db.execute('select id, description, author, price, paid from entries order by id desc')
    entries = [dict(pid=row[0], description=row[1], author=row[2], price=row[3], paid=row[4]) for row in cur.fetchall()]
    for e in entries:
        amount = e['price']
        e['price'] = cents_to_euros(amount)
    return render_template('show_entries.html', entries=entries)

@app.route('/get/entries')
def get_entries():
    cur = g.db.execute('select id, description, author, price, paid from entries order by id desc')
    entries = [dict(pid=row[0], description=row[1], author=row[2], price=row[3], paid=row[4]) for row in cur.fetchall()]
    for e in entries:
        amount = e['price']
        e['price'] = cents_to_euros(amount)
    return json.dumps(entries)

@app.route('/edit/<int:pid>/<action>', methods=['POST'])
def edit_entry(pid, action):
    if action == 'toggle_paid':
        cur = g.db.execute('SELECT paid from entries WHERE id=?', [pid])
        paid = cur.fetchone()[0]
        g.db.execute('UPDATE entries SET paid=? WHERE id=?', [not paid, pid])
        for q in queues:
            q.put(('toggle_paid', pid))
    if action == 'delete':
        g.db.execute('DELETE FROM entries WHERE id=?', [pid])
        for q in queues:
            q.put(('delete_entry', pid))
    g.db.commit()
    return redirect(url_for('show_entries'))

@app.route('/add', methods=['POST'])
def add_entry():
    description = request.form['description']
    author = request.form['author']
    price = re.findall('(\d+)(?:[,.](\d))?\s*(?:€|E)?', request.form['price'])

    if not description:
        return jsonify(msg='Please provide a description', type='error')
    elif not author:
        return jsonify(msg='Please provide your name', type='error')
    elif not price:
        return jsonify(msg='Price must be formed like this: 3.14', type='error')
    else:
        value = price[0]
        price = int(value[0]) * 100
        if value[1]:
            if len(value[1]) == 1:
                price += int(value[1]) * 10
            else:
                price += int(value[1])
        csr = g.db.execute('insert into entries (description, author, price, paid) values (?, ?, ?, ?)',
                [request.form['description'], request.form['author'], price, False])
        pid = csr.lastrowid
        g.db.commit()
        flash('A new entry has been posted', 'success')
        data = {'description': description,
                'author': author,
                'price': cents_to_euros(price),
                'paid': 0,
                'pid': pid} 
                
        for q in queues:
            q.put(('create_entry', data))
    return jsonify(msg='New entry added', type='success')

def wsgi_app(environ, start_response):  
    path = environ["PATH_INFO"]  
    if path == "/websocket":  
        handle_websocket(environ["wsgi.websocket"])
    else:  
        return app(environ, start_response)

queues = []

def handle_websocket(ws):
    q = gevent.queue.Queue()
    queues.append(q)
    while True:
        type, data = q.get()
        ws.send(json.dumps({'type': type, 'data': data}))

if __name__ == '__main__':
    http_server = WSGIServer((host, port), wsgi_app, handler_class=WebSocketHandler)
    print('Server started at %s:%s'%(host,port))
    http_server.serve_forever()