from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:Pass#1@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(300))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/blog', methods=['GET'])
def blog():
    post_id = request.args.get("id")
    if post_id == None:
        posts = Blog.query.all()
        page_title = "Build A Blog"
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
            return render_template('newpost.html', page_title='Add Blog Entry',
                blog_title=title, blog_body=body, 
                error_title=error_title, error_body=error_body)
        new_post = Blog(title, body)
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
        return render_template('newpost.html', page_title='Add Blog Entry',
            blog_title=title, blog_body=body, 
            error_title=error_title, error_body=error_body)

if __name__ == '__main__':
    app.run()