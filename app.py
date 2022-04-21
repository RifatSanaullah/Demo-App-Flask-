from sqlite3 import Cursor
from flask import Flask, Blueprint, request, flash, url_for, redirect, render_template
from requests import post
from sqlalchemy import desc
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, login_user
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_ui import get_swaggerui_blueprint
import json


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meetup.sqlite3'
app.config['SECRET_KEY'] = "random string"
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

### swagger specific ###
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Demo_app_using_flask"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
### end swagger specific ###


class meetups(db.Model):
   id = db.Column('meeting_id', db.Integer, primary_key=True)
   title = db.Column(db.String(100))
   description = db.Column(db.String(100))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))

def __init__(self, title, description):
   self.title = title
   self.description = description

@login_manager.user_loader
def load_user(id):
    # since the id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(id))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()
    # check if user actually exists
    # take the user supplied password, hash it, and compare it to the hashed password in database
    if not user or not check_password_hash(user.password, password): 
        flash('Please check your login details and try again.')
        return render_template('login.html') # if user doesn't exist or password is wrong, reload the page
   
    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return render_template('index.html', meetups = meetups.query.all())

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup_post():

    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again  
        flash('Email address already exists')
        return render_template('login.html')

    # create new user with the form data. Hash the password so plaintext version isn't saved.
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return render_template('login.html')

@app.route('/')
def index():
    return render_template('index.html', meetups = meetups.query.all())

@app.route('/meetup_all')
def meetup_all():
    my_dict = []
    my_dict_des = []
    my_dict_list = {}
    titles = [item.title for item in meetups.query.all()]
    for title_item in titles:
        my_dict.append(title_item)
    my_dict_list["Title"] = my_dict

    description = [item.description for item in meetups.query.all()]
    for des_item in description:
        my_dict_des.append(des_item)
    my_dict_list["description"] = my_dict_des

    with open("meetup_all.json", "w") as outfile:
     json.dump(my_dict_list, outfile)
    return my_dict_list

@app.route('/meetup_all/<int:id>')
def meetup_all_id(id):
    item_id_list = [item.title for item in meetups.query.filter_by(id=id)]
    des_id_list = [item.description for item in meetups.query.filter_by(id=id)]
    for item in item_id_list:
        print(item)
    for desItem in des_id_list:
        print(desItem)
    des = "Title:"+ " " + item + ", " + "Description:" + " "+ desItem
    return des

@app.route('/add_meetups')
def add_meetups():
    return render_template('add_meeting.html')

@app.route('/add_meetups', methods=['POST'])
def add_meetups_post():
    title = request.form.get('title')
    description = request.form.get('description')

    new_meeting = meetups(title = title, description = description)
    db.session.add(new_meeting)
    db.session.commit()
    return render_template('index.html', meetups = meetups.query.all())

@app.route('/meetup-details')
def meetup_details():
    titles = [item.title for item in meetups.query.all()]
    for item in titles:
        print(item)
    title = item
    description = [item.description for item in meetups.query.all()]
    for item in description:
        description = item
    return render_template('meetup-details.html', title = title, description = description)

if __name__ == '__main__':
   db.create_all()
   app.run(debug = True)
   