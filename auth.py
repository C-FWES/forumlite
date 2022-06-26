from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from app import db
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template("login.html")

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        flash('Try again.')
        return redirect(url_for('auth.login'))
    login_user(user, remember=remember)
    login_time = datetime.now()
    user.last_seen = login_time
    db.session.commit()
    return redirect(url_for('main.profile'))

@auth.route('/signup')
def signup():
    return render_template("signup.html")

@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    user = User.query.filter_by(email=email).first()

    if user:
        flash('User with this email already exists.')
        return redirect(url_for('auth.signup'))

    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))

@auth.route('/editprofile')
@login_required
def edit_profile():
    return render_template("edit_profile.html")

@auth.route('/editprofile', methods=['POST'])
def edit_profile_post():
    email = current_user.email
    new_email = request.form.get('email')
    new_name = request.form.get('name')
    user = User.query.filter_by(email=email).first()
    user.email = new_email
    user.name = new_name
    db.session.commit()
    return redirect(url_for('main.profile'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))
