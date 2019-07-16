from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(120))
    entry = db.Column(db.String(900))
    owner_id = db.Column(db.ForeignKey('user.id'))

    def __init__(self, blog_title, entry):
        self.blog_title = blog_title
        self.entry = entry
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.route("/signup", methods=['GET','POST'])
def signup():
  username = request.form['username']
  password = request.form['password']
  verify_pw = request.form['verify_pw']

  username_error = ''
  password_error = ''
  verify_pw_error = '' 

  if len(username) < 3:
    username_error = "Username must be between 3-20 characters long."

  if len(password) < 3:
    password_error = "Password must be between 3-20 characters."

  if verify_pw != password:
    verify_pw_error = "Does not match password."

  if username_error or password_error or verify_pw_error:
    username = username
    return render_template('signup.html', username=username, password=password, verify_pw=verify_pw,
    username_error=username_error, password_error=password_error, verify_pw_error=verify_pw_error)

  existing_user = User.query.filter_by(username=username).first()

  if existing_user:
    username_error = "Username already exists"
    return render_template('signup.html', username_error=username_error)
  
  if not existing_user:
    new_user = User(username, password)
    db.session.add(new_user)
    db.session.commit()
    session['username'] = username
    return redirect('/newpost')
  
  else:
    return render_template('signup.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        if 'username' not in session:
            return render_template("login.html")
        else:
            return redirect('/newpost')
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')

        if user and user.password != password:
            password_error = 'Incorrect Password'
            return render_template('login.html', password_error=password_error)

        if not user:
            username_error = 'Incorrect Username'
            return render_template('login.html', username_error=username_error)
        
    else:
        return render_template('login.html')


    

@app.route('/blog', methods=['POST','GET'])
def blog():

    if request.method == 'POST':
        blog_title = request.form['blog_title']
        entry = request.form['entry']
        new_blog = Blog(blog_title, entry)
        db.session.add(new_blog)
        db.session.commit()

        
        return render_template('blog.html',blog=new_blog)

    else:
        blog = Blog.query.filter_by(id=request.args.get('id')).first()
        print (blog)
        return render_template('blog.html', blog=blog)

@app.route('/', methods=['POST','GET'])
def home():
    blogs = Blog.query.all()
    return render_template('home.html', blogs=blogs)

@app.route('/newpost', methods=['POST','GET'])
def newpost():

    return render_template('newpost.html')

if __name__ == "__main__":
    app.run()