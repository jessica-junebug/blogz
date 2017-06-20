from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    text = db.Column(db.String(500))

    def __init__(self, title, text):
        self.title = title
        self.text = text

@app.route('/blog', methods=['GET'])
def show_posts():
    id = request.args.get('id')
    if id:
        post = Post.query.filter_by(id=id).first()
        title = post.title
        text = post.text
        return render_template('post.html',title=title, text=text)
    
    return render_template('blog.html', posts=Post.query.all())
    
@app.route('/newpost', methods=['POST', 'GET'])
def add_post():
    if request.method == 'POST':
        title = request.form['title']
        text = request.form['text']
        
        title_error = ""
        text_error = ""

        if not title:
            title_error = "Oops, forgot a blog title"
        elif not text:
            text_error = "Missing content"
        
        if title_error or text_error:
            return render_template('add-form.html', title=title, text=text, title_error=title_error, text_error=text_error)
        
        new_post = Post(title, text)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/blog?id={0}'.format(new_post.id))

    return render_template('add-form.html', title="", text="", title_error="", text_error="")    
    


if __name__ == '__main__':
    app.run()