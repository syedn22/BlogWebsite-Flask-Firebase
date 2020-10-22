from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pyrebase

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(app)


firebaseConfig = {
    "apiKey": "AIzaSyDv6WuyVD_A6nAc-UCrttOcHjYxf6ujQuc",
    "authDomain": "blog-app-fbe3f.firebaseapp.com",
    "databaseURL": "https://blog-app-fbe3f.firebaseio.com",
    "projectId": "blog-app-fbe3f",
    "storageBucket": "blog-app-fbe3f.appspot.com",
    "messagingSenderId": "964400661258",
    "appId": "1:964400661258:web:550f779ad51f30c1f3f0f3"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

user = auth.current_user


class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(20), nullable=False, default='N/A')
    date_posted = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow)

    def __repr__(self):
        return 'Blog post ' + str(self.id)


@app.route('/')
def Home():
    return render_template('Home.html')


@app.route('/logout')
def logout():
    auth.current_user = None
    return redirect('/posts')


@app.route('/changepassword', methods=['GET', 'POST'])
def changepassword():
    if auth.current_user == None:
        return redirect('/login')
    all_posts = BlogPost.query.order_by(BlogPost.date_posted).all()
    if auth.current_user:
        auth.send_password_reset_email(auth.current_user['email'])
        return render_template('profile.html', user=auth.current_user['email'], error="false", posts=all_posts)
    else:
        return redirect('/login')


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if auth.current_user == None:
        return redirect('/login')

    if request.method == 'POST':
        pass
    else:
        all_posts = BlogPost.query.order_by(BlogPost.date_posted).all()
        return render_template('profile.html', user=auth.current_user['email'], posts=all_posts)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['Password']
        confirmPassword = request.form['ConfirmPassword']
        if password == confirmPassword:
            try:
                result = auth.create_user_with_email_and_password(
                    email, password)
                user = auth.current_user
                return redirect("/posts")
            except:
                return "Failed to signup"
    else:
        return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['Password']
        try:
            result = auth.sign_in_with_email_and_password(email, password)
            user = auth.current_user
            return redirect("/posts")
        except:
            return "Failed to login"
    else:
        return render_template('login.html')


@app.route('/posts', methods=['GET', 'POST'])
def posts():
    if auth.current_user == None:
        user = ""
    else:
        user = auth.current_user['email']

    if request.method == 'POST':
        post_title = request.form['title']
        post_content = request.form['content']
        post_author = request.form['author']
        new_post = BlogPost(
            title=post_title, content=post_content, author=post_author)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/posts')
    else:
        all_posts = BlogPost.query.order_by(BlogPost.date_posted).all()
        return render_template('posts.html', posts=all_posts, user=user)


@app.route('/newPost')
def newPost():
    if auth.current_user == None:
        return redirect('/login')
    print(auth.current_user['email'])
    # user = auth.current_user.email
    if request.method == 'POST':
        post_title = request.form['title']
        post_content = request.form['content']
        # print(request.form['author'])
        post_author = request.form['author']
        new_post = BlogPost(
            title=post_title, content=post_content, author=post_author)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/posts')
    else:
        return render_template('newPost.html', author=auth.current_user['email'])


@app.route('/posts/delete/<int:id>')
def delete(id):
    post = BlogPost.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/posts')


@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):

    post = BlogPost.query.get_or_404(id)
    if request.method == 'POST':
        post.title = request.form['title']
        post.author = request.form['author']
        post.content = request.form['content']
        db.session.commit()
        return redirect('/posts')
    else:
        return render_template('edit.html', post=post)


if __name__ == "__main__":
    app.run(debug=True)
