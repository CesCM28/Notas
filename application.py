import functools
from logging import error
from flask import Flask
from flask import (
    Blueprint, blueprints, flash, g, render_template, request, url_for, session, redirect
)
from werkzeug.security import check_password_hash, generate_password_hash
from DB.db import get_db


application = Flask(__name__)
application.secret_key = "super secret key"

@application.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db, c = get_db()
        error = None
        c.execute(
            "SELECT id,username,password,name FROM user WHERE username like %s", (username,)
        )
        user = c.fetchone()

        print(user)

        if user is None:
            error = 'Usuario y/o contraseña invalida'
        #elif not check_password_hash(user['password'], password):
            #error = 'Usuario y/o contraseña invalida'
            

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('login.html')


# @application.before_app_request
# def load_logged_in_user():
#     user_id = session.get('user_id')

#     if user_id is None:
#         g.user = None 
#     else:
#         db, c = get_db()
#         c.execute(
#             "select * from users where id = ?", (user_id)
#         )
#         g.user = c.fetchone()

@application.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('index'))
        
        return view(**kwargs)

    return wrapped_view


@application.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()