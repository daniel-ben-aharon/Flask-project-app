import oauth as oauth
from authlib.integrations.flask_client import OAuth
from flask import Flask, render_template, url_for, redirect, session, request, flash
import music21

from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField   # BooleanField for checkbox
from wtforms.validators import InputRequired, Email, Length

from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy        # transfer data is in SQL into python objects
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'  # arbitrary value

Bootstrap(app)

class LoginForm(FlaskForm):            # inherit from FlaskForm
    username = StringField('username', validators=[InputRequired(),Length(min=3,max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8,max=80)])
    remember = BooleanField('remember me')


class RegisterForm(FlaskForm):
     email = StringField('email',validators=[InputRequired(),Email(message='Invalid email'),Length(max=50)])
     username = StringField('username',validators=[InputRequired(),Length(min=3,max=15)])
     password = PasswordField('password',validators=[InputRequired(), Length(min=8,max=80)])
     #create_time = PasswordField('password',validators=[InputRequired(), Length(min=8,max=80)])


# configure to mysql database
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////users.db' # users is name of our DB

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:YOUR_DB_PASSWORD@localhost/userdb' # userdb is name of our DB
app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'userdb'

db = SQLAlchemy(app)

# Create Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    date_added = db.Column(db.DateTime,default=datetime.utcnow ,nullable=False, unique=True)

    #Create a function to return a string when we add something
    def __repr__(self):
        return '<Name %r' % self.id


# oauth config
oauth = OAuth(app)
google = oauth.register(
    name='google',  # client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_id='1036027860865-hvb11o0o2is9co5ddmvu1mvrli7ejcif.apps.googleusercontent.com', #'1036027860865-urhmpve4q51gig9gu985n89tfpgr09qs.apps.googleusercontent.com',
    client_secret= os.getenv("GOOGLE_CLIENT_SECRET"),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    # userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    # This is only needed if using openId to fetch user info
    client_kwargs={'scope': 'openid email profile'},      #  scope=what we want google to give back using token and get method
)


# route direct to if the authentication was successful
@app.route('/authorize')
def authorize():
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    resp.raise_for_status()
    user_info = resp.json()
    # do something with the token and profile
    session['email'] = user_info['email']
    return redirect('/')


#  http://127.0.0.1:5000/    ip of machine
@app.route("/", methods=['GET','POST'])
@app.route("/home")
def home():
    if request.method == 'POST':
        # Fest form data
        userDetails = request.form
        name = userDetails['name']
        email = userDetails['email']
        password = userDetails['password']
        date = datetime.now()
        id = 1
        cur = db.connection.cursor()
        cur.execute("INSERT INTO users(username,email,password,create_time,id) VALUES(%s, %s, %s, %s, %d)",(name, email,password,date, id))
        db.connection.commit()
        cur.close()
        return 'success'

    return render_template('home.html')
    # n = music21.note.Note("G5")
    # return "<p>" + n.name + "</p>"


# Route for handling the login page with google account
@app.route("/loginWithGoogle")
def loginWithGoogle():
    google = oauth.create_client('google')
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route("/login", methods=['GET','POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():    #  check to works if form is submitted
        return '<h1>' + form.username.data + ' ' + form.password.data + '<h1>'

    return render_template('login.html',form=form)


@app.route("/signin", methods=['GET', 'POST'])        # register
def signin():
   form = RegisterForm()
   name = None
   if form.validate_on_submit():
       user = Users.query.filter_by(email=form.email.data).first()
       if user is None:
           user = Users(name=form.username.data, email=form.email.data, password=form.password.data)
           # # Hash the password!!!
           # hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
           # user = Users(username=form.username.data, name=form.name.data, email=form.email.data,
           #              favorite_color=form.favorite_color.data, password_hash=hashed_pw)
           db.session.add(user)
           db.session.commit()
       name = form.username.data

       # clean the form
       form.username.data = ''
       form.password.data = ''
       form.email.data = ''
       # form.favorite_color.data = ''
       # form.password_hash.data = ''

       flash("User Added Successfully!")
       our_users = Users.query.order_by(Users.date_added)
       return render_template("add_user.html",
                          form=form,
                          name=name,
                          our_users=our_users)

   '''''''''
   msg = ''
   if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
       username = request.form['username']
       password = request.form['password']
       email = request.form['email']
       cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
       cursor.execute('SELECT * FROM accounts WHERE username = % s', (username,))
       account = cursor.fetchone()
       if account:
           msg = 'Account already exists !'
       elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
           msg = 'Invalid email address !'
       elif not re.match(r'[A-Za-z0-9]+', username):
           msg = 'Username must contain only characters and numbers !'
       elif not username or not password or not email:
           msg = 'Please fill out the form !'
       else:
           cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, password, email,))
           mysql.connection.commit()
           msg = 'You have successfully registered !'
   elif request.method == 'POST':
       msg = 'Please fill out the form !'
   return render_template('register.html', msg=msg)
   '''''''''''

   # if request.method == 'POST':
   #     # Fest form data
   #     userDetails = request.form
   #     name = userDetails['name']
   #     email = userDetails['email']
   #     password = userDetails['password']
   #     date = datetime.now()
   #     id = 1
   #     cur = db.connection.cursor()
   #     cur.execute("INSERT INTO user(username,email,password,create_time,id) VALUES(%s, %s, %s, %s, %d)",
   #                 (name, email, password, date, id))
   #     db.connection.commit()
   #     cur.close()
   #     return 'success'
   #
   # # if form.validate_on_submit():    #  check to works if form is submitted
   #     cur.execute("INSERT INTO user(username,email,password,create_time,id) VALUES(%s, %s, %s, %s, %d)",
   #                 (form.username.data, form.email.data, form.password.data, date, id))

   #     return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '<h1>'

   return render_template('signin.html',form=form)


@app.route('/logout')
def logout():
    for key in list(session.key()):
        session.pop(key)
    return redirect('/')


@app.route("/about")
def about():
    return render_template('about.html', title='About')


if __name__ == '__main__':
    app.run(debug=True)
