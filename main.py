from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY'] = True

db = SQLAlchemy(app)

app.secret_key ='blogz123'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(120))
    entry = db.Column(db.String(900))
    owner_id = db.Column(db.ForeignKey('user.id'))

    def __init__(self, blog_title, entry, owner_id):
        self.blog_title = blog_title
        self.entry = entry
        self.owner_id = owner_id

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

#User must be logged in to write a blog post
@app.before_request
def require_login():
    allowed_routes = ['index','blog','login','signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

#if they are not already a user
@app.route("/signup", methods=['GET','POST'])
def signup():
    if request.method == 'POST':

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

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')
    

@app.route('/blog', methods=['POST','GET'])
def blog():

    if "user" in request.args:
        user_id = request.args.get("user")
        user = User.query.get(user_id)
        user_blogs = Blog.query.filter_by(owner=user).all()
        return render_template("single_user.html", page_title = user.username + "'s Posts!", 
        user_blogs=user_blogs)
    
    single_post = request.args.get('id')
    if single_post:
        blog = Blog.query.get(single_post)
        return render_template("viewpost.html", blog=blog)

    else:
        blogs = Blog.query.all()
        return render_template('blog.html', page_title="All Blog Posts", blogs=blogs)

@app.route('/', methods=['POST','GET'])
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/newpost', methods=['POST','GET'])
def newpost():

    if request.method == 'GET':
        return render_template('newpost.html')

    if request.method == 'POST':
        blog_title = request.form['blog_title']
        entry = request.form['entry']

    title_error = ''
    entry_error = ''

    if len(blog_title) == 0:
        title_error = "Add a title for your post!"
    
    if len(entry) == 0:
        entry_error = "You didn't write a blog dummy."

    if title_error or entry_error:
        return render_template('newpost.html', titlebase="New Entry", title_error=title_error,
        entry_error=entry_error, blog_title=blog_title, entry=entry)

    else:
        if len(blog_title) and len(entry) > 0:
            owner_id = User.query.filter_by(username=session['username']).first().id
            new_entry = Blog(blog_title, entry, owner_id)
            db.session.add(new_entry)
            db.session.commit()
            return redirect('/blog?id=' + str(new_entry.id))


if __name__ == "__main__":
    app.run()