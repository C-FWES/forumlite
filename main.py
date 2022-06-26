from flask import Blueprint, render_template
from app import db
from flask_login import login_required, current_user

main = Blueprint('main', __name__)

@main.route('/profile')
@login_required
def profile():
    return render_template("profile.html", name=current_user.name, email=current_user.email, time=current_user.last_seen)

