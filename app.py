from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_required, current_user
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

db = SQLAlchemy()

app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

from models import User, Post, Comment, Reply, ReplyThread

with app.app_context():
    db.create_all()
    db.session.commit()

from auth import auth as auth_blueprint

app.register_blueprint(auth_blueprint)

from main import main as main_blueprint

app.register_blueprint(main_blueprint)


@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except:
        return None


@app.route('/')
def home():  # put application's code here
    return render_template("index.html")


@app.route('/writepost')
@login_required
def write_post():
    return render_template("write_post.html")


@app.route('/create_post', methods=['POST'])
def create_post():
    poster = current_user.id
    title = request.form.get('input-title')
    content = request.form.get('input-content')
    new_post = Post(title=title, content=content, poster_id=poster)
    db.session.add(new_post)
    db.session.commit()
    return redirect(url_for('posts'))


@app.route('/posts')
@login_required
def posts():
    posts = Post.query.order_by(Post.date_posted)
    return render_template("posts.html", posts=posts)


@app.route('/posts/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    comments = Comment.query.order_by(Comment.timestamp)
    replies = Reply.query.order_by(Reply.timestamp)
    reply_threads = ReplyThread.query.order_by(ReplyThread.timestamp)
    specific_comments = [comment for comment in comments if comment.post_id == id]
    return render_template("post.html", post=post, comments=specific_comments, replies=replies,
                           reply_threads=reply_threads, reply_thread_continued=reply_threads)


@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    id = current_user.id
    if id == post.poster_id:
        if request.method == 'POST':
            new_title = request.form.get('input-title')
            new_content = request.form.get('input-content')
            post.title = new_title
            post.content = new_content
            db.session.commit()
            return redirect(url_for('posts'))
        return render_template("edit_post.html", post=post)


@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    id = current_user.id
    if id == post.poster_id:
        try:
            db.session.delete(post)
            db.session.commit()
            posts = Post.query.order_by(Post.date_posted)
            return render_template("posts.html", posts=posts)
        except:
            # error handler
            posts = Post.query.order_by(Post.date_posted)
            return render_template("posts.html", posts=posts)


@app.route('/post/<int:id>/comment', methods=['POST'])
@login_required
def post_comment(id):
    post = Post.query.get_or_404(id)
    commenter = current_user.id
    content = request.form.get('comment_body')
    new_comment = Comment(content=content, author_id=commenter, post_id=post.id)
    db.session.add(new_comment)
    db.session.commit()
    return redirect(url_for('post', id=post.id))


@app.route('/post/<int:id>/comment/edit', methods=['GET', 'POST'])
def edit_comment(id):
    comment = Comment.query.get_or_404(id)
    id = current_user.id
    if id == comment.author_id:
        if request.method == 'POST':
            new_content = request.form.get('comment-body')
            comment.content = new_content
            db.session.commit()
            return redirect(url_for('post', id=comment.post_id))
        return render_template("edit_comment.html", comment=comment)


@app.route('/post/<int:id>/comment/delete', methods=['GET', 'POST'])
def delete_comment(id):
    comment = Comment.query.get_or_404(id)
    saved_id = comment.post_id
    id = current_user.id
    if id == comment.author_id:
        try:
            db.session.delete(comment)
            db.session.commit()
            comments = Comment.query.order_by(Comment.timestamp)
            return redirect(url_for('post', id=saved_id))
        except:
            comments = Comment.query.order_by(Comment.timestamp)
            return redirect(url_for('post', id=saved_id))


@app.route('/post/<int:id>/comment/reply', methods=['GET', 'POST'])
def reply_comment(id):
    comment = Comment.query.get_or_404(id)
    post_id = comment.post_id
    if request.method == 'POST':
        reply_content = request.form.get('reply_body')
        replyer = current_user.id
        new_reply = Reply(reply_author_id=replyer, content=reply_content, comment_id=comment.id, post_id=post_id)
        db.session.add(new_reply)
        db.session.commit()
        return redirect(url_for('post', id=comment.post_id))
    return render_template("reply.html", comment=comment)


@app.route('/post/<int:id>/comment/reply/edit', methods=['GET', 'POST'])
def edit_reply(id):
    reply = Reply.query.get_or_404(id)
    id = current_user.id
    parent_name = Comment.query.get_or_404(reply.comment_id).author_name.name
    if id == reply.reply_author_id:
        if request.method == 'POST':
            new_content = request.form.get('reply_body')
            reply.content = new_content
            db.session.commit()
            return redirect(url_for('post', id=reply.post_id))
        return render_template("edit_reply.html", reply=reply, parent_name=parent_name)


@app.route('/post/<int:id>/comment/reply/delete', methods=['GET', 'POST'])
def delete_reply(id):
    reply = Reply.query.get_or_404(id)
    saved_id = reply.post_id
    id = current_user.id
    if id == reply.reply_author_id:
        try:
            db.session.delete(reply)
            db.session.commit()
            replies = Reply.query.order_by(Reply.timestamp)
            return redirect(url_for('post', id=saved_id))
        except:
            comments = Reply.query.order_by(Reply.timestamp)
            return redirect(url_for('post', id=saved_id))


@app.route('/post/<int:id>/comment/reply/reply_thread', methods=['GET', 'POST'])
def reply_thread(id):
    reply = Reply.query.get_or_404(id)
    main_reply_id = reply.id
    if request.method == 'POST':
        reply_thread_content = request.form.get('reply_body')
        replyer = current_user.id
        new_reply_thread = ReplyThread(author_id=replyer, content=reply_thread_content, reply_id=reply.id,
                                       post_id=reply.post_id)
        db.session.add(new_reply_thread)
        db.session.commit()
        return redirect(url_for('post', id=reply.post_id))
    return render_template("reply_thread.html", reply=reply)

@app.route('/post/<int:id>/comment/reply/reply_thread/edit', methods=['GET', 'POST'])
def edit_reply_thread(id):
    reply = ReplyThread.query.get_or_404(id)
    saved_id = reply.post_id
    id = current_user.id
    parent_name = Reply.query.get_or_404(reply.reply_id).reply_author_name.name
    if id == reply.author_id:
        if request.method == 'POST':
            new_content = request.form.get('reply_body')
            reply.content = new_content
            db.session.commit()
            return redirect(url_for('post', id=saved_id))
        return render_template("edit_reply_thread.html", reply=reply, parent_name=parent_name)


@app.route('/post/<int:id>/comment/reply/reply_thread/delete', methods=['GET', 'POST'])
def delete_reply_thread(id):
    reply = ReplyThread.query.get_or_404(id)
    saved_id = reply.post_id
    id = current_user.id
    if id == reply.author_id:
        try:
            db.session.delete(reply)
            db.session.commit()
            replies = ReplyThread.query.order_by(ReplyThread.timestamp)
            return redirect(url_for('post', id=saved_id))
        except:
            replies = ReplyThread.query.order_by(ReplyThread.timestamp)
            return redirect(url_for('post', id=saved_id))


@app.route('/post/<int:id>/comment/reply/reply_thread/reply_thread_continued', methods=['GET', 'POST'])
def reply_thread_continue(id):
    reply = ReplyThread.query.get_or_404(id)
    parent_reply_id = reply.id
    if request.method == 'POST':
        reply_thread_content = request.form.get('reply_body')
        replyer = current_user.id
        depth_curr = 0
        if reply.depth:
            depth_curr = int(reply.depth) + 2
        new_reply_thread = ReplyThread(author_id=replyer, content=reply_thread_content, reply_id=reply.reply_id,
                                       post_id=reply.post_id, parent_id=reply.id, depth=depth_curr)
        db.session.add(new_reply_thread)
        db.session.commit()
        return redirect(url_for('post', id=reply.post_id))
    return render_template("reply_thread_continue.html", reply=reply)


if __name__ == '__main__':
    app.run()
