
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing

import re

DATABASE = './pizza.sqlite3'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)

app.config.from_envvar('PIZZA_SETTINGS', silent=True)

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
    entries = [dict(id=row[0], description=row[1], author=row[2], price=row[3], paid=row[4]) for row in cur.fetchall()]
    for e in entries:
        amount = e['price']
        e['price'] = '{},{:02d} €'.format(int(amount / 100), amount % 100)
    return render_template('show_entries.html', entries=entries)

@app.route('/delete', methods=['POST'])
def delete_entry():
    pid = request.form['pid']
    pass

@app.route('/add', methods=['POST'])
def add_entry():
    description = request.form['description']
    author = request.form['author']
    price = re.findall('(\d+)(?:[,.](\d))?\s*(?:€|E)?', request.form['price'])

    if not description:
        flash('Please provide a description', 'error')
    elif not author:
        flash('Please provide your name', 'error')
    elif not price:
        flash('Price must be formed like this: 3.14', 'error')
    else:
        value = price[0]
        price = int(value[0]) * 100
        if value[1]:
            if len(value[1]) == 1:
                price += int(value[1]) * 10
            else:
                price += int(value[1])
        g.db.execute('insert into entries (description, author, price, paid) values (?, ?, ?, ?)',
                [request.form['description'], request.form['author'], price, False])
        g.db.commit()
        flash('A new entry has been posted', 'success')
    return redirect(url_for('show_entries'))

if __name__ == '__main__':
    app.run()
