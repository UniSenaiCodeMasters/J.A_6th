from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Senha', validators=[DataRequired()])
    remember = BooleanField('Lembrar de Mim')
