import flask
import linkbook_user as lu
from flask import Flask, render_template, session
import flask_login
from flask_pymongo import MongoClient
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.secret_key = "thalooslinkbooktest"

client = MongoClient('localhost:27017')
db = client.UserData

db.UserData.insert_one(
            {
            "id": "thaloo@linkbook.com",
            "name":"Thaloo Jack White",
            "pasword":"park7591"
            })

login_manager = flask_login.LoginManager()
login_manager.init_app(app)


users = {'thaloo@linkbook.com': {'password': 'park7591'}}

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if flask.request.method == 'GET':
        if session.get('logged_in') == True:
            return flask.redirect(flask.url_for('protected'))
        else:
            return render_template('login_form.html')

    email = flask.request.form['email']
    if flask.request.form['password'] == users[email]['password']:
        user = lu.User(email)
        flask_login.login_user(user)
        return flask.redirect(flask.url_for('protected'))

    return 'Bad login'
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('index.html')

@app.route('/user_info')
@flask_login.login_required
def protected():
    session['logged_in'] = True
    return render_template('user_info.html',email=flask_login.current_user.email)

@app.route('/logout',methods=['POST'])
def logout():
    flask_login.logout_user()
    session.pop('logged_in', None)
    return flask.redirect(flask.url_for('hello_world'))

@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return

    user = lu.User(email)
    return user


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return

    user = lu.User(email)

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = request.form['password'] == users[email]['password']

    return user

@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'

if __name__ == '__main__':
    app.run()
