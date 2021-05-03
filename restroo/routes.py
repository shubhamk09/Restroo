<<<<<<< HEAD
import nltk as nltk
from flask import render_template, url_for, flash, redirect, request, abort
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer

from restroo import app, db, bcrypt
from restroo.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, ReviewForm
from restroo.models import User, Post, Review
from flask_login import login_user, current_user, logout_user, login_required
import secrets
import os
from PIL import Image

nltk.download('vader_lexicon')

nltk.download('stopwords')
set(stopwords.words('english'))


@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, username=form.username.data, address=form.address.data,
                    email=form.email.data, password=hashed_password, contact=form.contact.data, role=form.role.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)
    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.username = form.username.data
        current_user.contact = form.contact.data
        current_user.address = form.address.data
        current_user.role = form.role.data
        db.session.commit()
        flash('Your data have been updated successfully', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.contact.data = current_user.contact
        form.address.data = current_user.address
        form.role.data = current_user.role
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, category=form.category.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your Post have been Created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form, legend='New Post')


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.category = form.category.data
        db.session.commit()
        flash('Your Post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        form.category.data = post.category
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your Post has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route("/user_post/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('user_post.html', posts=posts, user=user)


@app.route("/review/new/<int:rest_id>", methods=['GET', 'POST'])
@login_required
def new_review(rest_id):
    form = ReviewForm()

    def sentiment(text1):
        stop_words = stopwords.words('english')
        processed_doc1 = ' '.join([word for word in text1.split() if word not in stop_words])
        sa = SentimentIntensityAnalyzer()
        dd = sa.polarity_scores(text=processed_doc1)
        compound = round((1 + dd['compound']) / 2, 2)

        return compound

    if form.validate_on_submit():
        text1 = form.content.data.lower()
        compound = sentiment(text1)
        rest = User.query.filter_by(id=rest_id).first_or_404()
        review = Review(title=form.title.data, content=form.content.data, sentiment=compound,
                        reviewer=current_user, reviewplace=rest)
        db.session.add(review)
        db.session.commit()
        flash('Your Review have been Created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_review.html', title='New Review', form=form, legend='New Review')


@app.route("/reviews/<int:rest_id>")
def reviews(rest_id):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(id=rest_id).first_or_404()
    reviews = Review.query.filter_by(reviewplace=user).order_by(Review.date_posted.desc()).paginate(page=page,
                                                                                                    per_page=5)
    return render_template('reviews.html', reviews=reviews, rest_id=rest_id)


@app.route("/review/<int:review_id>")
def review(review_id):
    review = Review.query.get_or_404(review_id)
    return render_template('review.html', title=review.title, review=review)


@app.route("/review/<int:review_id>/delete", methods=['POST'])
@login_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    if review.reviewer != current_user:
        abort(403)
    db.session.delete(review)
    db.session.commit()
    flash('Your Review has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route("/review/<int:review_id>/update", methods=['GET', 'POST'])
@login_required
def update_review(review_id):
    review = Review.query.get_or_404(review_id)
    if review.reviewer != current_user:
        abort(403)
    form = ReviewForm()
    if form.validate_on_submit():
        review.title = form.title.data
        review.content = form.content.data
        db.session.commit()
        flash('Your Review has been updated!', 'success')
        return redirect(url_for('review', review_id=review.id))
    elif request.method == 'GET':
        form.title.data = review.title
        form.content.data = review.content
    return render_template('create_review.html', title='Update Review', form=form, legend='Update Review')
=======
import nltk as nltk
from flask import render_template, url_for, flash, redirect, request, abort
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer

from restroo import app, db, bcrypt
from restroo.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, ReviewForm
from restroo.models import User, Post, Review
from flask_login import login_user, current_user, logout_user, login_required
import secrets
import os
from PIL import Image

nltk.download('vader_lexicon')

nltk.download('stopwords')
set(stopwords.words('english'))


@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, username=form.username.data, address=form.address.data,
                    email=form.email.data, password=hashed_password, contact=form.contact.data, role=form.role.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)
    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.username = form.username.data
        current_user.contact = form.contact.data
        current_user.address = form.address.data
        current_user.role = form.role.data
        db.session.commit()
        flash('Your data have been updated successfully', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.contact.data = current_user.contact
        form.address.data = current_user.address
        form.role.data = current_user.role
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, category=form.category.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your Post have been Created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form, legend='New Post')


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.category = form.category.data
        db.session.commit()
        flash('Your Post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        form.category.data = post.category
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your Post has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route("/user_post/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('user_post.html', posts=posts, user=user)


@app.route("/review/new/<int:rest_id>", methods=['GET', 'POST'])
@login_required
def new_review(rest_id):
    form = ReviewForm()

    def sentiment(text1):
        stop_words = stopwords.words('english')
        processed_doc1 = ' '.join([word for word in text1.split() if word not in stop_words])
        sa = SentimentIntensityAnalyzer()
        dd = sa.polarity_scores(text=processed_doc1)
        compound = round((1 + dd['compound']) / 2, 2)

        return compound

    if form.validate_on_submit():
        text1 = form.content.data.lower()
        compound = sentiment(text1)
        rest = User.query.filter_by(id=rest_id).first_or_404()
        review = Review(title=form.title.data, content=form.content.data, sentiment=compound,
                        reviewer=current_user, reviewplace=rest)
        db.session.add(review)
        db.session.commit()
        flash('Your Review have been Created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_review.html', title='New Review', form=form, legend='New Review')


@app.route("/reviews/<int:rest_id>")
def reviews(rest_id):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(id=rest_id).first_or_404()
    reviews = Review.query.filter_by(reviewplace=user).order_by(Review.date_posted.desc()).paginate(page=page,
                                                                                                    per_page=5)
    return render_template('reviews.html', reviews=reviews, rest_id=rest_id)


@app.route("/review/<int:review_id>")
def review(review_id):
    review = Review.query.get_or_404(review_id)
    return render_template('review.html', title=review.title, review=review)


@app.route("/review/<int:review_id>/delete", methods=['POST'])
@login_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    if review.reviewer != current_user:
        abort(403)
    db.session.delete(review)
    db.session.commit()
    flash('Your Review has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route("/review/<int:review_id>/update", methods=['GET', 'POST'])
@login_required
def update_review(review_id):
    review = Review.query.get_or_404(review_id)
    if review.reviewer != current_user:
        abort(403)
    form = ReviewForm()
    if form.validate_on_submit():
        review.title = form.title.data
        review.content = form.content.data
        db.session.commit()
        flash('Your Review has been updated!', 'success')
        return redirect(url_for('review', review_id=review.id))
    elif request.method == 'GET':
        form.title.data = review.title
        form.content.data = review.content
    return render_template('create_review.html', title='Update Review', form=form, legend='Update Review')
>>>>>>> 79a153c7800c90e0ce83ecab0b5b77ae1b98b817
