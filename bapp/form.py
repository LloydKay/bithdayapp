from flask_wtf import FlaskForm
 
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired,Email

 
class LoginForm(FlaskForm):
    username=StringField('Username',validators=[Email('Haba, enter email now')])
    password=PasswordField('Password',validators=[DataRequired('Your Password is a must')])
    
    terms = BooleanField('Agree?')
    submit = SubmitField('Login')