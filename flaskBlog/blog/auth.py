from flask import Blueprint, render_template, redirect, url_for, request, flash
from . import db
from .models import User, NForm
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from config import mail_username, mail_password


auth = Blueprint("auth", __name__)
mail = Mail()


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password): # the hashed password first, then the plain text password.
                flash("You're in!", category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password', category='error')
        else:
            flash('User does not exist.', category='error')

    return render_template('login.html', user=current_user)


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username') # we use get so that if the data or field (i.e, username) doesn't exist,
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password1 = request.form.get('password1')   # it returns 'None' instead of thrashing the code.
        password2 = request.form.get('password2')

        email_exists = User.query.filter_by(email=email).first()
        username_exists = User.query.filter_by(username=username).first()

        if email_exists:
            flash('Email is already taken.', category='error')  # this will flash a message
        elif username_exists:
            flash('Username is already taken.', category='error')
        elif password1 != password2:
            flash("Passwords don't match.", category='error')
        elif len(username) < 4:
            flash('Username is too short.', category='error')
        elif len(password1) < 6:
            flash('Password is too short.', category='error')
        else:
            new_user = User(email=email, username=username, first_name=first_name, last_name=last_name,
                            password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)    # adds to the 'staging area' for db
            db.session.commit()         # puts it into the db
            login_user(new_user, remember=True)
            flash("You're in!")
            return redirect(url_for('views.home'))

    return render_template('signup.html', user=current_user)


@auth.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        msg = Message(subject=f'(You got mail from {name}', body=f'Name: {name}\n Email:{email}\n\n{message}',
                      sender=mail_username, recipients=['iamjuben@gmail.com'])
        mail.send(msg)
        flash("Message Sent! I'll get back to you shortly.", category='success')

    return render_template('contact.html', user=current_user, success=True)


@auth.route('/about', methods=['GET', 'POST'])
def about():
    name = None     # since there won't be a name the first time the page loads
    form = NForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
    return render_template('about.html', name=name, form=form, user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.home')) # reffing the fn 'home' under the blueprint 'views'
