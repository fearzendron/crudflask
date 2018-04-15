# Fernando Zendron - RM79684
#
# Aplicação foi criada usando Flask
#
#
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'rm79684.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)



def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')


@app.route('/')
def show_entries():
    db = get_db()

    search_word = str(request.args.get('search',""))
    filter_access_level = str(request.args.get('access_level',""))

    if search_word:
        if filter_access_level:
            print("1")
            cur = db.execute('select id, full_name, small_name, access_level, role, last_access_date, last_access_hour '
                             'from users where small_name LIKE ? and access_level = ?', ("%" + search_word + "%", str(filter_access_level), ))
        else:
            print("2")
            cur = db.execute('select id, full_name, small_name, access_level, role, last_access_date, last_access_hour '
                             'from users where small_name LIKE ?', ("%" + search_word + "%",))
    else:
        if filter_access_level:
            print("3")
            cur = db.execute('select * from users where access_level = ?', (str(filter_access_level),))
        else:
            print("4")
            cur = db.execute('select id, full_name, small_name, access_level, role, last_access_date, last_access_hour '
                         'from users order by id desc')

    users = cur.fetchall()
    total_users = get_total_users()

    return render_template('show_entries.html', entries=users, qtd_users=total_users)



@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    try:
        db.execute('insert into users (full_name, small_name, access_level, role) values (?, ?, ?, ?)',
                 [request.form['full_name'], request.form['small_name'], request.form['access_level'], request.form['role']])
        db.commit()
        flash('Novo usuário adicionado')
    except:
        flash('Usuário ja cadastrado!')
    return redirect(url_for('show_entries'))

@app.route('/search', methods=['GET'])
def search_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    cur = db.execute('select * from users where small_name like %?%',
                 [request.form['search']])
    users = cur.fetchall()
    return render_template('show_entries.html', entries=users)

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
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

# return the total number of users inside database
def get_total_users():
    db = get_db()
    cur = db.execute('select count(*) from users ')
    total = cur.fetchone()[0]
    return total