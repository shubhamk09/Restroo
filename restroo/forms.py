from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, RadioField, TextAreaField, SelectField, \
    MultipleFileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from restroo.models import User
from flask_login import current_user


class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    address = StringField('Address', validators=[DataRequired()])
    contact = StringField('Contact', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    role = RadioField('Restaurant or Customer', choices=[('customer', 'Customer'), ('restaurant', 'Restaurant')])
    table = StringField('Number of tables available')
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    address = StringField('Address', validators=[DataRequired()])
    contact = StringField('Contact', validators=[DataRequired()])
    role = RadioField('Restaurant or Customer', choices=[('customer', 'Customer'), ('restaurant', 'Restaurant')])
    picture = FileField('Update profile picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    catt = ['Fundraising', 'Festivals', 'Community Events', 'Social Events', 'Virtual Event', 'Corporate Events']
    category = SelectField('Category', choices=catt, validators=[DataRequired()])
    submit = SubmitField('Post')


class ReviewForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')


class BookingForm(FlaskForm):
    number_of_table = StringField('Number of Tables you want to book', validators=[DataRequired()])
    submit = SubmitField('Book')


class MediaForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    media = FileField('Update profile picture',render_kw={'multiple': True})
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Add')
