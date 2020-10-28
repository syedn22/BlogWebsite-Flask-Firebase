from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pyrebase

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(app)
firebaseConfig = {
    "apiKey": "AIzaSyB4nvrWnoscwQfC-fbArplFtKcYritUNIc",
    "authDomain": "jsrapp-daca2.firebaseapp.com",
    "databaseURL": "https://jsrapp-daca2.firebaseio.com",
    "projectId": "jsrapp-daca2",
    "storageBucket": "jsrapp-daca2.appspot.com",
    "messagingSenderId": "8813826011",
    "appId": "1:8813826011:web:b9b117e1a1b4b71bbfa1fe"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
database = firebase.database()

user = auth.current_user
database = firebase.database()


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
    all_posts = getPosts()
    if auth.current_user:
        auth.send_password_reset_email(auth.current_user['email'])
        return render_template('profile.html', user=auth.current_user['email'], error="false", posts=all_posts)
    else:
        return redirect('/login')


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if auth.current_user == None:
        return redirect('/login')

    if request.method == 'GET':
        all_posts = getPosts()
        return render_template('profile.html', user=auth.current_user['email'], posts=all_posts)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['Password']
        confirmPassword = request.form['ConfirmPassword']
        if len(password) < 8:
            return render_template('signup.html', error=True)

        if password == confirmPassword:
            try:
                result = auth.create_user_with_email_and_password(
                    email, password)
                print(result)
                return redirect("/posts")
            except:
                return render_template('signup.html', error=True)

    else:
        return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['Password']
        if len(password) < 8:
            return render_template('login.html', error=True)
        try:
            result = auth.sign_in_with_email_and_password(email, password)
            return redirect("/posts")
        except:
            return auth.current_user

    else:
        return render_template('login.html')


@app.route('/posts', methods=['GET'])
def posts():
    if auth.current_user == None:
        return render_template('login.html')

    if request.method == 'GET':
        all_posts = getPosts()
        return render_template('posts.html', posts=all_posts, user=auth.current_user['email'])


@app.route('/newPost', methods=['POST', 'GET'])
def newPost():
    if auth.current_user == None:
        return redirect('/login')

    if request.method == 'POST':
        post_title = request.form['title']
        post_content = request.form['content']
        post_author = request.form['author']
        temp = {"title": post_title,
                "author": post_author, "content": post_content}
        putPost(temp)
        return redirect('/posts')
    else:
        return render_template('newPost.html', author=auth.current_user['email'])


@app.route('/posts/delete/<string:id>')
def delete(id):
    print(id)
    database.child("posts").child(id).remove()
    return redirect('/posts')


@app.route('/posts/edit/<string:id>', methods=['GET', 'POST'])
def edit(id):
    post = getPost(id)
    if request.method == 'POST':
        post_title = request.form['title']
        post_author = request.form['author']
        post_content = request.form['content']
        temp = {"title": post_title,
                "author": post_author, "content": post_content}
        updatePost(temp, id)
        return redirect('/posts')
    else:
        return render_template('edit.html', post=post)

@app.route('/posts/comment/<string:id>',methods=['GET', 'POST'])
def comment(id):
    if request.method == 'POST':
        comment = request.form['comment']        
        putComment(comment,id)
        return redirect('/posts')
    else:
        return redirect('/posts')

def getPost(id):
    post = database.child("posts").child(id).get(
        token=auth.current_user['idToken']).val()
    post['id'] = database.child("posts").child(id).get(
        token=auth.current_user['idToken']).key()

    return post


def getPosts():
    all_posts = database.child("posts").get(token=auth.current_user['idToken'])
    posts = []
    for post in all_posts:
        temp = post.val()
        temp['id'] = post.key()
        posts.append(temp)
    return posts


def putPost(data):
    database.child("posts").push(
        data=data, token=auth.current_user['idToken'])


def updatePost(data, id):
    database.child("posts").child(id).update(
        data=data, token=auth.current_user['idToken'])

def putComment(message,id):
    comment={}
    comment['id']=auth.current_user['email']
    comment['comment']=message
    print(comment)
    database.child("posts").child(id).child("comments").push(data=comment, token=auth.current_user['idToken'])
    

if __name__ == "__main__":
    app.run(debug=True)
