from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from .models import Post, User, Comment, Like
from . import db

views = Blueprint("views", __name__)


@views.route('/')
@views.route('/home')
@login_required
def home():
    posts = Post.query.all()
    return render_template('home.html', user=current_user, posts=posts)


@views.route('/createpost', methods=['GET', 'POST'])
@login_required
def createpost():
    if request.method == 'POST':
        text = request.form.get('text')

        if not text:
            flash('Post cannot be empty', category='error')
        else:
            post = Post(text=text, author=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash('Post created!', category='success')
            return redirect(url_for('views.home'))

    return render_template('createpost.html', user=current_user)


@views.route('/editpost/<id>', methods=['GET', 'POST'])
@login_required
def editpost(id):
    post = Post.query.get_or_404(id)
    if post.user != current_user:
        abort(404)
    if request.method == 'POST':
        post.text = request.form.get('text')
        if not post.text:
            flash('Field cannot be empty', category='error')
        else:
            post = Post(text=post.text, author=current_user.id)
            db.session.commit()
            flash('Post Updated')
            return redirect(url_for('views.home'))

    return render_template('edit_post.html', user=current_user)


@views.route('/delete-post/<id>') # this is called a dynamic path, whereby we pass variables inside the angle brackets.
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first() # .first to get first result

    try:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted!', category='success')
        return redirect(url_for('views.home'))
    except:
        flash('You do not have permission to delete this post.', category='error')
        return redirect(url_for('views.home'))


@views.route('/posts/<username>')
@login_required
def posts(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash('User does not exist.', category='error')
        return redirect(url_for('views.home'))

    posts = user.posts
    return render_template('posts.html', user=current_user, posts=posts, username=username)


@views.route('/create-comment/<post_id>', methods=['POST'])
@login_required
def create_comment(post_id):
    text = request.form.get('text')

    if not text:
        flash("Comment box cannot be left empty.", category='error')
    else:
        post = Post.query.filter_by(id=post_id)
        if post:
            comment = Comment(text=text, author=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
            flash('Comment added.', category='success')
        else:
            flash('Cannot find post.')

    return redirect(url_for('views.home'))


@views.route('/delete-comment/<comment_id>')
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()

    if not comment:
        flash("Comment cannot be found.", category='error')
    elif current_user.id != comment.author and current_user.id != comment.post_author:
        flash('You are not authorized to delete this comment.', category='error')
    else:
        db.session.delete(comment)
        db.session.commit()

    return redirect(url_for('views.home'))


@views.route('/like-post/<post_id>', methods=['GET'])
@login_required
def like_post(post_id):
    post = Post.query.filter_by(id=post_id).first()
    like = Like.query.filter_by(author=current_user.id, post_id=post_id).first()

    if not post:
        flash("Post doesn't exist.", category='error')
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(author=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()

    return redirect(url_for('views.home'))

