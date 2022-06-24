from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

db = SQLAlchemy()

app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

db.init_app(app)

from auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

from main import main as main_blueprint
app.register_blueprint(main_blueprint)

@app.route('/')
def home():  # put application's code here
    return render_template("index.html")


if __name__ == '__main__':
    app.run()
