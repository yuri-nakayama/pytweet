# inherting db, creating the database table, creating modes
from pytweet.database import db

from datetime import datetime
from flask_login import UserMixin

followtable = db.Table('followtable', 
              db.Column('source_user_id', db.Integer, db.ForeignKey('users.id'), index=True), 
              db.Column('target_user_id', db.Integer, db.ForeignKey('users.id'), index=True), 
              db.UniqueConstraint('source_user_id', 'target_user_id', name='unique_friendships'))

class User(db.Model, UserMixin): # this UserMixin is for our login to keep the session data

  __tablename__ = 'users'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), nullable=False)
  password = db.Column(db.String(100), nullable=False)
  email =  db.Column(db.String(200), nullable=True)
  bio =  db.Column(db.String(280), nullable=True)
  
  create_at = db.Column(db.DateTime, nullable=False, default=datetime.now) 
  update_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

  posts = db.relationship(('Posts'), backref="editor_posts", lazy=True)
  comments = db.relationship(('Comments'), backref="editor_comments", lazy=True)
  friendship = db.relationship(('Friendships'), backref="friendships", lazy=True)

  friends = db.relationship('User', 
        secondary=followtable, 
        primaryjoin=(followtable.c.source_user_id==id),
        secondaryjoin=(followtable.c.target_user_id==id),
        backref=db.backref("users", lazy="dynamic"), lazy="dynamic")
        # primaryjoin=id==friendship.c.source_user_id, 
        # secondaryjoin=id==friendship.c.target_user_id)
  # select * from user join followtable on user.id = followtable.source_user_id

  def follow (self, friend):  # friend, the argument is User instance
    if friend not in self.friends:
      self.friends.append(friend)
      # friend.friends.append(self)

  def un_follow(self, friend):
    if friend in self.friends:
        self.friends.remove(friend)
        # friend.friends.remove(self)

  # def is_following (self, user):
  #   return self.friends.fileter(followtable.c.target_user_id==user.id).all()

class Posts(db.Model):

  __tablename__ = 'posts'

  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
  title = db.Column(db.String(30), nullable=False)
  content = db.Column(db.String(280), nullable=False)

  create_at = db.Column(db.DateTime, nullable=False, default=datetime.now) 
  update_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

  comments = db.relationship(('Comments'), backref="author", lazy=True)

class Comments(db.Model):

  __tablename__ = 'comments'

  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
  post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
  comment = db.Column(db.String(280), nullable=False)

  create_at = db.Column(db.DateTime, nullable=False, default=datetime.now) 
  update_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

class Friendships(db.Model):

  __tablename__ = 'friendships'

  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer)
  user_following_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

  create_at = db.Column(db.DateTime, nullable=False, default=datetime.now) 
  update_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

# from pytweet.database import db # you cannot overwrite the database using this command, this is only good for final table
# db.create_all() # use for making a table

# flask db init - it means we are initializing the database
# flask db migrate - migrating our model to our database
# flask db upgrade - finalizing the migration between model and database
