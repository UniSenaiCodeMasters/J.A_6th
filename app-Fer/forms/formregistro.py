from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import DataRequired, Email, Length

class UserCreationForm(FlaskForm):
    username = StringField('Nome do usuário', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=5)])
    role = SelectField('Papel', choices=[('admin', 'Admin'), ('usuariopadrao', 'Usuário Padrão')], validators=[DataRequired()])