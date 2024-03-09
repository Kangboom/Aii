from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileRequired

class RegisterForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    useremail = StringField('useremail', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()]) #equalTo("필드네임")
    allergy = TextAreaField('allergy')

class UserLoginForm(FlaskForm):
    useremail = StringField('useremail', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])

class UploadForm(FlaskForm):
    file_front = FileField('file_front', validators=[FileRequired()])
    file_back = FileField('file_back', validators=[FileRequired()])
    submit = SubmitField('submit')