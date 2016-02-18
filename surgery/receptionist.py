# all the imports
from contextlib import closing
import sqlite3

from flask import (g, session, request, render_template, abort, redirect, flash,
                   url_for, )
from flask import Flask

import pliers


# configuration
DATABASE = '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'
UPLOAD_FOLDER = 'results'
ALLOWED_EXTENSIONS = set('txt')


# create our little application :)
app = Flask(__name__, static_url_path='')
app.config.from_object(__name__)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


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
        'select query, depth, link from queries order by id desc')
    queries = [dict(query=row[0], depth=row[1], link=row[2])
               for row in cur.fetchall()]
    return render_template('show_queries.html', queries=queries)


@app.route('/results')
def show_results():
    cur = g.db.execute(
        'select query, depth, link from queries order by id desc')
    queries = [dict(query=row[0], depth=row[1], link=row[2])
               for row in cur.fetchall()]
    return render_template('show_results.html', queries=queries)


@app.route('/add', methods=['POST'])
def make_query():
    if not session.get('logged_in'):
        abort(401)
    results_link = pliers.linkify(request.form['query'])
    g.db.execute('insert into queries (query, depth, link) values (?, ?, ?)',
                 [request.form['query'],
                  request.form['depth'],
                  results_link])
    g.db.commit()
    # start the query running
    with open('static/teeth/{}'.format(results_link), 'w') as placeholder:
        placeholder.write('Still waiting for results')
    pliers.main(request.form['query'], request.form['depth'])
    flash('New query was successfully started')
    return redirect(url_for('show_queries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_queries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_queries'))


if __name__ == '__main__':
    app.run()
