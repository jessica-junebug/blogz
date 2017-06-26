from flask import request, redirect, render_template, session, flash
from app import SQLAlchemy, db, app
from model import Post, User

@app.before_request
def require_login():
    public_pages = ['index', 'show_post', 'login', 'show_posts', 'user_signup']
    if request.endpoint not in public_pages and 'username' not in session:
        return redirect('/login')

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', users=User.query.all())

@app.route('/blog', methods=['GET'])
def show_posts():
    user = request.args.get('user')
    if user:
        user = User.query.filter_by(username=user).first()
        posts = user.posts
        return render_template('single_user.html', posts=posts)


    id = request.args.get('id')
    if id:
        post = Post.query.filter_by(id=id).first()
        title = post.title
        text = post.text
        username = post.owner.username
        return render_template('post.html', title=title, text=text, username=username)
    
    return render_template('blog.html', posts=Post.query.all())

@app.route('/newpost', methods=['POST', 'GET'])
def add_post():
    if request.method == 'POST':
        title = request.form['title']
        text = request.form['text']
        
        user = User.query.filter_by(username=session['username']).first()

        if not title:
            flash("Oops, forgot a blog title")
            return redirect('/newpost')
        elif not text:
            flash("Missing content")
            return redirect('/newpost')

        new_post = Post(title, text, user)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/blog?id={0}'.format(new_post.id))

    return render_template('add-form.html', title="", text="")

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/')
        else:
            flash("Invalid Username or Password")

    return render_template('/login.html', username='', password='')

@app.route('/signup', methods=['POST','GET'])
def user_signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        vpass = request.form['vpass']

        username_error = ''
        password_error = ''

        if username == "":
            username_error += "Username required"
        elif " " in username:
            username_error += "Username must contain no spaces"
        elif not (len(username) > 3 and len(username) < 20):
            username_error = username_error + "Username must be 3-20 characters"

        if " "in password:
            password_error += "Please mind the gap"
        elif not (len(password) > 3 and len(password) < 20):
            password_error += "Password must be 3-20 characters"
        elif not password == vpass:
            password_error += "Go fish"

        if username_error or password_error:
            flash(username_error + "          " + password_error)
            return redirect('/signup')

        existing_user = User.query.filter_by(username=username).first()

        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            flash("You are now registered")
            return redirect('/newpost')
        else:
            flash('Username already exists')
            return redirect('/signup')

    return render_template('signup.html', username='', password='', vpass='',)

@app.route('/logout', methods=['GET'])
def logout():
    del session['username']
    flash("Logged Out")
    return redirect('/')



if __name__ == '__main__':
    app.run()