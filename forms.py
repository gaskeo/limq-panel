#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    email = StringField("Электропочта", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    remember_me = BooleanField("Запомнить меня")

    submit = SubmitField("Войти")


class RegisterForm(FlaskForm):
    email = StringField("Электропочта", validators=[DataRequired()])
    username = StringField("Ваше имя", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    password_again = PasswordField("Еще раз пароль", validators=[DataRequired()])
    submit = SubmitField("Зарегистрироваться")


class RegisterChannelForm(FlaskForm):
    name = StringField("Название", validators=[DataRequired()])
    submit = SubmitField("Создать канал")


class CreateKeyForm(FlaskForm):
    channel = StringField("Канал", validators=[DataRequired()])
    read = BooleanField("Чтение", false_values=["0"])
    write = BooleanField("Запись", false_values=["0"])
