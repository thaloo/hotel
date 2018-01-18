import flask
import linkbook_user as lu
from flask import Flask, render_template, session
import flask_login
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "thalooslinkbooktest"

mongo = PyMongo(app)
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

users={}

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if flask.request.method == 'GET':
        if session.get('logged_in') == True:
            return flask.redirect(flask.url_for('protected'))
        else:
            return render_template('index.html')

    email = flask.request.form['email']
    try:
        user_id = mongo.db.profiles.find_one_or_404({"email":email})
    except:
        print("User "+email+" Not Found!")
        return flask.redirect(flask.url_for('hello_world'))
    if check_password_hash(mongo.db.profiles.find_one({"email":email})['password'],flask.request.form['password']):
        user = lu.User(email)
        flask_login.login_user(user)
        users[email] = mongo.db.profiles.find_one({"email":email})['password']
        return flask.redirect(flask.url_for('protected'))

    return flask.redirect(flask.url_for('hello_world'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if flask.request.method == 'GET':
        return render_template('user_register.html')
    email = flask.request.form['email']
    try:
        user_id = mongo.db.profiles.find_one_or_404({"email":email})
    except:
        print("User "+email+" Not Found!")
        r_email = flask.request.form['email']
        r_password = generate_password_hash(flask.request.form['password'])
        r_name = flask.request.form['name']

        try:
            mongo.db.profiles.insert_one({
                "email":r_email,
                "password":r_password,
                "name":r_name
            })
        except:
            print("Error during insertion data!!!!")
        return flask.redirect(flask.url_for('hello_world'))
    return render_template('user_register.html')

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
    user.is_authenticated = check_password_hash(users[email]['password'],request.form['password'])

    return user
@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'

if __name__ == '__main__':
    app.run("0.0.0.0", port = 80)
