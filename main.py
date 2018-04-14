from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:Pass#1@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

app.secret_key = 'y337kGcys&zP3B'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(300))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

    def __repr__(self):
        return '<Blog %r>' % self.title

@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            if user.password == password:
                session['username'] = username
                return redirect('/newpost')
            else:
                flash('Incorrect password', 'error')
                return redirect('/login')
        else:
            flash('Username does not exist', 'error')
            return redirect('/login')
    else:
        return render_template('login.html', page_title="Login")

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        if username == "":
            flash('One or more fields are invalid (blank)', 'error')
            return redirect('/signup')
        elif  password == "" or verify == "":
            flash('One or more fields are invalid (blank)', 'error')
            return redirect('/signup')
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists', 'error')
            return redirect('/signup')
        if len(username) < 3:
            flash('Invalid username', 'error')
            return redirect('/signup')
        if len(password) < 3:
            flash('Invalid password', 'error')
            return redirect('/signup')
        if password != verify:
            flash('Passwords do not match', 'error')
            return redirect('/signup')
        new_user = User(username, password)
        db.session.add(new_user)
        db.session.commit()
        session['username'] = username
        return redirect('/newpost')
    else:
        return render_template('signup.html', page_title="Signup")

@app.route('/blog', methods=['GET'])
def blog():
    post_id = request.args.get("id")
    post_user = request.args.get("user")
    if post_id == None:
        if post_user == None:
            posts = Blog.query.all()
        else:
            user_id = User.query.filter_by(username=post_user).first()
            posts = Blog.query.filter_by(owner=user_id).all()
        page_title = "blog posts!"
    else:
        posts = Blog.query.filter_by(id=post_id).all()
        page_title = ""
    return render_template('blog.html', page_title=page_title, posts=posts)    

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        error_title = ""
        error_body = ""
        if title == "":
            error_title = "Please fill in the title"
        if body == "":
            error_body = "Please fill in the body"
        if error_title != "" or error_body != "": 
            return render_template('newpost.html', page_title='new post',
                blog_title=title, blog_body=body, 
                error_title=error_title, error_body=error_body)
        owner = User.query.filter_by(username=session['username']).first()
        new_post = Blog(title, body, owner)
        db.session.add(new_post)
        db.session.flush()
        id = str(new_post.id)
        db.session.commit()
        return redirect('/blog?id='+ id)

    if request.method == 'GET':
        title = ""
        body = ""
        error_title = ""
        error_body = ""
        return render_template('newpost.html', page_title='new post',
            blog_title=title, blog_body=body, 
            error_title=error_title, error_body=error_body)

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', page_title='blog users!', users=users)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

if __name__ == '__main__':
    app.run()