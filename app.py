from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user
from flask_migrate import Migrate

app = Flask(__name__)

db = SQLAlchemy()

app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

from models import User, Post

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
    return render_template("post.html", post=post)

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
            #error handler
            posts = Post.query.order_by(Post.date_posted)
            return render_template("posts.html", posts=posts)



if __name__ == '__main__':
    app.run()
