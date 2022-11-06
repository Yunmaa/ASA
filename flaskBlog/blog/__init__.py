from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_mail import Mail, Message
from config import mail_password, mail_username


db = SQLAlchemy()
DB_NAME = 'database.db'
mail = Mail()


# first thing to do whenever creating a flask app
def create_app():
    app = Flask(__name__)   # name is reffing the name of the module you'll run to create the app.
    mail.init_app(app)
    app.config['SECRET_KEY'] = "hiyapeeps"
    # for initializing the db
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['MAIL_SERVER'] = 'smtp-mail.outlook.com'
    app.config['PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = mail_username
    app.config['MAIL_PASSWORD'] = mail_password
    db.init_app(app)

    # for registering the blueprints
    from .views import views    # this is a relative import because I am inside a python package, trying to import
    from .auth import auth      # another file also inside it, (hence the dot).

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Post, Comment, Like

    login_manager = LoginManager()  # so the user doesn't have to enter username/password everytime they want to log in
    login_manager.login_view = 'auth.login'  # means if someone's not logged in, and tries to access a page,
    login_manager.init_app(app)              # we redirect to auth.login

    @login_manager.user_loader  # this uses a session to store the id of a user that is logged in
    def load_user(id):  # a session is temp, (default lasts 30 days), but you can choose how long you want it to last
        return User.query.get(int(id))

    create_database(app)

    return app


def create_database(app):
    if not path.exists('blog/' + DB_NAME):
        with app.app_context():
            db.create_all()
        print('Database Created!')
