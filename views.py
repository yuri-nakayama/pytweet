# contains our functions to connect HTML and Python¥

from flask import Flask, render_template, request, redirect, url_for, flash      # importing necssary flask modules
from .app import app                  # connection to app.py
from .database import db              # connection to db
from passlib.hash import sha256_crypt # encryping the password - to change random strings
# pip3 install passlib
from .models.models import User, Posts, Comments, Friendships       # importing the models - to access the models
from flask_login import login_user, LoginManager, login_required, current_user, logout_user   # this is for our login session and we will use the flask_login module

login_manager = LoginManager() # creating an object of class LoginManager()
login_manager.init_app(app) # passing the parameter and initialize app inseide the login_manager

@app.route("/test/friendship")
def friendship():
  user = User.query.filter_by(name="yuri").first()
  usertofollow = User.query.filter_by(name="sample").first()
  user.follow(usertofollow)
  db.session.add(user)  # inserting to the table
  db.session.commit()   # commit
  return render_template("test.html")

  # user = User.query.filter_by(id=current_user.id).first()
  # following = user.is_following(user)

  # return render_template("test.html", following=following)

@app.route("/")
def home():
  return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():

  if request.method == "POST":
    username = request.form["username"]
    password = request.form["password"]

    user = User(name=username, password=sha256_crypt.encrypt(password)) # encryption
    db.session.add(user)  # inserting to the table
    db.session.commit()   # commit

    return redirect("/") # just URL

  return render_template("register.html") # URL and to pass the data

@app.route("/login", methods=["GET", "POST"])
def login():

  if request.method == "POST":
    username = request.form["username"]
    password = request.form["password"]

    user = User.query.filter_by(name=username).first()
    # print(user.__dict__)
    # first() method is just for querying the first data that it finds that has the same value
    # filter_by : used for simple queries on the column names
    # fileter   : The same can be accomplished with filter but instead uses the '==' equality operator 

    if user is not None and user.name == username:
      validate = sha256_crypt.verify(password, user.password) # comparing the input data and the database data
      if validate == True:
        login_user(user) # Flask
      else:
        flash(u'Invalid Password Provided','login_error') # 
        return redirect("/") # just URL

    else:
      flash(u'User Is not yet registered','login_error')
      flash(u'username is incorrect!','login_error')
      return redirect("/") # just URL

  # return redirect("/timeline", user=user.id)
  return redirect(url_for('timeline', id=user.id)) # to go to route directly and it is allowed to put only one argument

@app.route('/logout')
@login_required
def logout():
  logout_user()
  return redirect("/") # just URL

@login_manager.user_loader # checking the user and its id, so that it can access the /timeline
def load_user(id):         # this means checking the id of the user that can access the /timeline
  return User.query.get(int(id)) # flask wants to know the current data

@app.route("/timeline/<int:id>")
@login_required            # this decorator is for login required
def timeline(id):

  in_claus_val = []
  in_claus_val.append(id)

  friends = Friendships.query.filter_by(user_id=id).all()
  if friends is not None:
    for friend in friends:
      in_claus_val.append(friend.user_following_id)

  # posts = Posts.query.filter_by(user_id=id).order_by(Posts.id.desc()).all()
  # posts = Posts.query.filter_by(user_id=id).all()
  posts = Posts.query.filter(Posts.user_id.in_(in_claus_val)).order_by(Posts.update_at.desc()).all()
  print(posts)
  # comments = Comments.query.filter_by(user_id=id).all()

  # return render_template("timeline.html", posts=posts, comments=comments)
  return render_template("timeline.html", posts=posts)

@app.route("/add_post/<int:id>", methods=["GET", "POST"])
def add_post(id):

  if request.method == "POST":
    user_id = id
    title = request.form["title"]
    content = request.form["content"]

    post = Posts(user_id=user_id, title=title, content=content)
    db.session.add(post)  # inserting to the table
    db.session.commit()   # commit

  flash(u'New Tweet','tweet_successful')
  return redirect(url_for('timeline', id=id)) # to go to route directly and it is allowed to put only one argument

@app.route("/get_post/<int:id>")
def get_post(id):

  post = Posts.query.filter_by(id=id).first()

  if post is None:
    return redirect(url_for('timeline', id=current_user.id)) # to go to route

  return render_template("upd_post.html", post=post)

@app.route("/upd_post/<int:id>", methods=["GET", "POST"])
def upd_post(id):

  if request.method == "POST":

    # checking if the data is existed
    post = Posts.query.filter_by(id=id).first()
    if post is None:
      return redirect(url_for('timeline', id=current_user.id)) # to go to route

    post.title = request.form["title"]
    post.content = request.form["content"]

    db.session.commit()   # commit/persists/finalize those changes to the database

  flash(u'Update Tweet','tweet_successful')
  return redirect(url_for('timeline', id=current_user.id)) # to go to route

@app.route("/del_post/<int:id>")
def del_post(id):

  comments = Comments.query.filter_by(post_id=id).all()
  if comments is not None:
    # return redirect(url_for('timeline', id=id)) # to go to route
    for comment in comments:
      db.session.delete(comment)
      # db.session.commit()   # commit/persists/finalize those changes to the database

  post = Posts.query.filter_by(id=id).first()
  if post is None:
    return redirect(url_for('timeline', id=id)) # to go to route

  db.session.delete(post)
  db.session.commit()   # commit/persists/finalize those changes to the database

  flash(u'Delete Tweet','tweet_successful')
  return redirect(url_for('timeline', id=current_user.id)) # to go to route

"""
In naming a function there is naming convention
def updateUser(): camelCase
class UpdateUser(): FascalCase
update_user : snake_case
"""

@app.route("/get_user/<int:id>")
def get_user(id):
# ex) def displayProfileGetUser(id):

  user = User.query.filter_by(id=id).first()

  if user is None:
    return redirect(url_for('timeline', id=id)) # to go to route

  return render_template("profile.html", user=user)

@app.route("/upd_user/<int:id>", methods=["GET", "POST"])
def upd_user(id):

  if request.method == "POST":

    # checking if the data is existed
    user = User.query.filter_by(id=id).first()
    if user is None:
      return redirect(url_for('timeline', id=id)) # to go to route

    user.name = request.form["username"]
    user.email = request.form["email"]
    user.bio = request.form["bio"]

    db.session.commit()   # commit/persists/finalize those changes to the database

  return redirect(url_for('timeline', id=id)) # to go to route

@app.route("/get_user2/<int:id>")
def get_user2(id):

  user = User.query.filter_by(id=id).first()

  if user is None:
    return redirect(url_for('profile', id=id)) # to go to route

  return render_template("password.html", user=user)

@app.route("/del_user/<int:id>", methods=["GET", "POST"])
def del_user(id):

  if request.method == "POST":

    # checking if the data is existed
    user = User.query.filter_by(id=id).first()
    if user is None:
      return redirect(url_for('profile', id=id)) # to go to route

    password = request.form["password"]

    validate = sha256_crypt.verify(password, user.password)
    if validate == False:
      return redirect(url_for('password', id=id)) # Error msg

    db.session.delete(user)
    db.session.commit()   # commit/persists/finalize those changes to the database

  return redirect("/") # just URL

@app.route("/add_comment/<int:id>", methods=["GET", "POST"])
def add_comment(id):

  if request.method == "POST":
    user_id = id
    post_id = request.form["post_id"]
    comment = request.form["comment"]

    query = Comments(user_id=user_id, post_id=post_id, comment=comment)
    db.session.add(query)  # inserting to the table
    db.session.commit()   # commit

  flash(u'Add Comment','tweet_successful')
  return redirect(url_for('timeline', id=id)) # to go to route directly and it is allowed to put only one argument

@app.route("/del_comment/<int:id>")
def del_comment(id):

  # checking if the data is existed
  comment = Comments.query.filter_by(id=id).first()
  if comment is None:
    return redirect(url_for('timeline', id=current_user.id)) # to go to route

  db.session.delete(comment)
  db.session.commit()   # commit/persists/finalize those changes to the database

  flash(u'Delete Comment','tweet_successful')
  return redirect(url_for('timeline', id=current_user.id)) # to go to route

@app.route("/get_comment/<int:id>")
def get_comment(id):

  comment = Comments.query.filter_by(id=id).first()

  if comment is None:
    flash(u'Error Update Comment','tweet_error')
    return redirect(url_for('timeline', id=current_user.id)) # to go to route

  return render_template("upd_comment.html", comment=comment)

@app.route("/upd_comment/<int:id>", methods=["GET", "POST"])
def upd_comment(id):

  if request.method == "POST":

    # checking if the data is existed
    comment = Comments.query.filter_by(id=id).first()
    if comment is None:
      flash(u'Error Update Comment','tweet_error')
      return redirect(url_for('timeline', id=current_user.id)) # to go to route

    comment.comment = request.form["text"]

    db.session.commit()   # commit/persists/finalize those changes to the database

  flash(u'Update Comment','tweet_successful')
  return redirect(url_for('timeline', id=current_user.id)) # to go to route

@app.route("/get_following/<int:id>")
def get_following(id):

  # user = User.query.filter_by(name=username).first() 
  users = User.query.all() 

  if users is None:
    return redirect("/") # just URL

  return render_template("following.html", users=users)

@app.route("/get_follower/<int:id>")
def get_follower(id):

  # user = User.query.filter_by(name=username).first() 
  users = User.query.all() 

  if users is None:
    return redirect("/") # just URL

  return render_template("follower.html", users=users)

@app.route("/searchUser", methods=["GET", "POST"])
def searchUser():

  if request.method == "POST":
    tag = request.form["search"]
    search = "%{}%".format(tag)

    users = User.query.filter(User.name.like(search)).all()
    if users is None:
      print(users)
      flash(u'No User Data','tweet_error')
      return redirect(url_for('timeline', id=current_user.id)) # to go to route

  return render_template("user.html", users=users)

@app.route("/add_following/<int:id>")
def add_following(id):

  target_user = User.query.get(id)
  current_user.follow(target_user)
  db.session.commit()   # commit

  flash('Suceess following','tweet_successful')
  return redirect(url_for('timeline', id=current_user.id)) # to go to route

@app.route("/del_following/<int:id>")
def del_following(id):

  target_user = User.query.get(id)
  current_user.un_follow(target_user)
  db.session.commit()      # commit

  flash('Suceess Unfollowing','tweet_successful')
  return redirect(url_for('timeline', id=current_user.id)) # to go to route
