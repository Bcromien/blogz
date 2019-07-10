from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://buildablog:buildablog@localhost:8889/buildablog'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(120))
    entry = db.Column(db.String(500))

    def __init__(self, blog_title, entry):
        self.blog_title = blog_title
        self.entry = entry

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

@app.route('/', methods=['GET'])
def home():
    blogs = Blog.query.all()
    return render_template('home.html', blogs=blogs)

@app.route('/newpost', methods=['GET'])
def newpost():
    return render_template('newpost.html')

if __name__ == "__main__":
    app.run()