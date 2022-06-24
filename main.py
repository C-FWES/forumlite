from flask import Blueprint
from app import db

main = Blueprint('main', __name__)

@main.route('/profile')
def profile():
    return 'Profile'