from app import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    last_seen = db.Column(db.String(100))
    posts = db.relationship('Post', backref='poster')

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
    poster_id = db.Column(db.Integer, db.ForeignKey(User.id))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(256))
    comments = db.relationship('Comment', backref='commented_post')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey(User.id))
    author_name = db.relationship('User', backref='comment_poster')
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey(Post.id))
    replies = db.relationship('Reply', backref='replied_comment')

class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reply_author_id = db.Column(db.Integer, db.ForeignKey(User.id))
    reply_author_name = db.relationship('User', backref='reply_poster')
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    comment_id = db.Column(db.Integer, db.ForeignKey(Comment.id))
    post_id = db.Column(db.Integer, db.ForeignKey(Post.id))
    replies = db.relationship('ReplyThread', backref='replied_thread')

class ReplyThread(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey(User.id))
    author_name = db.relationship('User', backref='reply_thread_poster')
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    reply_id = db.Column(db.Integer, db.ForeignKey(Reply.id))
    parent_id = db.Column(db.Integer, db.ForeignKey('reply_thread.id'))
    children = db.relationship('ReplyThread', backref='parent', remote_side=[id])
    post_id = db.Column(db.Integer, db.ForeignKey(Post.id))
    depth = db.Column(db.Integer, default=1)


