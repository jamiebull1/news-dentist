# all the imports
from contextlib import closing
import hashlib
import os
import random
import sqlite3
import time

from flask import (g, session, request, render_template, abort, redirect, flash,
                   url_for, send_from_directory)
from flask import Flask

from surgery import pliers, keys
from surgery import toothcomb, stickers


THIS_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_DIR = os.path.join(THIS_DIR, "static")

app = Flask(__name__, static_url_path='')
app.config.from_object(keys)


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
def show_queries():
    cur = g.db.execute(
        "select username, query, depth, link, timestr from queries "
        "order by id desc")
    queries = [dict(query=row[1], depth=row[2], link=row[3], timestr=row[4])
               for row in cur.fetchall()]
    return render_template('show_queries.html', queries=queries)


@app.route('/stats/<path:path>')
def send_stats(path):
    text = toothcomb.Text(path)
    stats = {'top10': text.most_common(10),
             'top50': text.most_common(50),
             'top100': text.most_common(100)
             }
    print(path)
    cur = g.db.execute(
        "select query from queries where link = '{}'".format(path))
    stats['query'] = cur.fetchall()[0][0]
    # render a wordcloud
    png_name = path[:-4] + '.png'
    stats['wordcloud'] = png_name

    stickers.generate(path, png_name)

    return render_template('show_stats.html', stats=stats)


@app.route('/teeth/<path:path>')
def send_result(path):
    teeth_dir = os.path.join(STATIC_DIR, 'teeth')
    return send_from_directory(teeth_dir, path)


@app.route('/add', methods=['POST'])
def make_query():
    if not session.get('logged_in'):
        abort(401)
        
    timestr = time.strftime("%Y/%m/%d %H:%M:%S")
    results_link = pliers.linkify(request.form['query'], timestr)
    g.db.execute(
        'insert into queries '
        '(username, query, depth, stopwords, minlength, link, timestr) '
        'values (?, ?, ?, ?, ?, ?, ?)',
        [session.get('user'),
         request.form['query'],
         request.form['depth'],
         request.form['minlength'],
         '',
         results_link,
         timestr,
         ])
    g.db.commit()
    # start the query running
    res = pliers.main(request.form['query'],
                request.form['depth'],
                results_link,
                minlength=request.form['minlength'],
                cookie=request.form['cookie']
                )
    if res:
        print(res['captcha'])
        return redirect(res['captcha'])
        
    flash('See, that wasn\'t so bad was it?')
    return redirect(url_for('show_queries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        cur = g.db.execute("select username from users")
        users = [row[0] for row in cur.fetchall()]
        print(users)
        cur = g.db.execute(
            "select hashpass from users "
            "where username='{}'".format(request.form['username']))
        hashpass = [row[0] for row in cur.fetchall()]
        if request.form['username'] not in users:
            error = 'Invalid username'
        elif hashed(request.form['password']) not in hashpass:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            session['user'] = request.form['username']
            flash('The dentist will see you now')
            return redirect(url_for('show_queries'))
    return render_template('login.html', error=error)


def hashed(password):
    p = str(password).encode('utf8')
    hashed = hashlib.md5(p)
    return hashed.hexdigest()


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        # is username already in database?
        cur = g.db.execute("select username, email from users")
        users = [row[0] for row in cur.fetchall()]
        emails = [row[1] for row in cur.fetchall()]
        if request.form['username'] in users:
            error = 'Username already exists'
        elif request.form['email'] in emails:
            error = 'Email is already registered'
        elif request.form['password'] != request.form['password2']:
            error = 'Passwords don\'t match'
        else:
            g.db.execute(
                'insert into users (username, email, hashpass) values '
                '(?, ?, ?)',
                [request.form['username'],
                 request.form['email'],
                 hashed(request.form['password'])
                 ])
            g.db.commit()
            session['logged_in'] = True
            session['user'] = request.form['username']
            flash('You were logged in')
            return redirect(url_for('show_queries'))
    return render_template('login.html', error=error)


@app.route('/recover', methods=['GET', 'POST'])
def recover():
    error = None
    if request.method == 'POST':
        # is email already in database?
        cur = g.db.execute("select username, email from users")
        users = [row[0] for row in cur.fetchall()]
        emails = [row[1] for row in cur.fetchall()]
        if request.form['email'] and request.form['email'] not in emails:
            error = 'No account exists for that email'
        elif request.form['username'] and request.form['username'] not in users:
            error = 'No account exists for that user'
        else:
            recoverkey = random.getrandbits(128)
            print(recoverkey)
            print(request.form['email'])
            if request.form['email']:
                g.db.execute(
                    "update users set hashpass=? where email=?",
                    [hashed(recoverkey),
                     request.form['email']
                     ])
            elif request.form['username']:
                g.db.execute(
                    "update users set hashpass=? where username=?",
                    [hashed(recoverkey),
                     request.form['username']
                     ])

            g.db.commit()
            session['logged_in'] = False
            flash('A recovery password has been sent to your email address')
            return redirect(url_for('login'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_queries'))
