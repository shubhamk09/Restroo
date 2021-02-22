from datetime import datetime
from restroo import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.Text, nullable=False)
    contact = db.Column(db.Integer, nullable=False)
    role = db.Column(db.String(20), nullable=False, default="customer")
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    # Relationships
    table = db.relationship('Tables', backref='restaurant', lazy=True)
    medias = db.relationship('Media', backref='uploader', lazy=True)
    posts = db.relationship('Post', back_populates='author', lazy=True)
    bookings = db.relationship('Booking', back_populates='booker', lazy=True,
                               primaryjoin='User.id==Booking.cust_id')
    reserves = db.relationship('Booking', back_populates='bookplace', lazy=True,
                               primaryjoin='User.id==Booking.rest_id')
    reviewed_by = db.relationship('Review', back_populates='reviewer', lazy=True,
                                  primaryjoin='User.id==Review.cust_id')
    reviewed_at = db.relationship('Review', back_populates='reviewplace', lazy=True,
                                  primaryjoin='User.id==Review.rest_id')

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(20), nullable=False)
    rest_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Relationships
    author = db.relationship('User', back_populates='posts')

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


class Tables(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total = db.Column(db.Integer, nullable=False)
    available = db.Column(db.Integer, nullable=False)
    rest_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


class Media(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    rest_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    number_of_table = db.Column(db.Integer, nullable=False)
    cust_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rest_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Relationships
    booker = db.relationship('User', back_populates='bookings', foreign_keys='Booking.cust_id')
    bookplace = db.relationship('User', back_populates='reserves', foreign_keys='Booking.rest_id')

    def __repr__(self):
        return f"Post('{self.number_of_table}', '{self.date_posted}')"


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    sentiment = db.Column(db.String(120), nullable="False")
    rest_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    cust_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    reviewer = db.relationship('User', back_populates='reviewed_by', foreign_keys='Review.cust_id')
    reviewplace = db.relationship('User', back_populates='reviewed_at', foreign_keys='Review.cust_id')

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"
