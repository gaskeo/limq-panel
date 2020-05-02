#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, HiddenField, RadioField
from wtforms.validators import DataRequired, Length


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


class MainSettingsChannelForm(FlaskForm):
    id = HiddenField("", validators=[DataRequired()])
    name = StringField("Название", validators=[DataRequired(), Length(
        min=1, max=20, message="Не больше 20 символов")])
    is_active = BooleanField("Активен", validators=[DataRequired()])

    submit = SubmitField("Сохранить изменения")


class CreateKeyForm(FlaskForm):
    id = HiddenField("", validators=[DataRequired()])
    name = StringField("Название", validators=[DataRequired(), Length(
        min=1, max=20, message="Не больше 20 символов")])
    permissions = RadioField("", choices=[('0', 'Прием'), ('1', 'Отправка')], default='1')
    info_allowed = BooleanField("Разрешить info", false_values=["0"])
    submit = SubmitField("Создать ключ")


class CreateMixin(FlaskForm):
    channel = HiddenField("", validators=[DataRequired()])
    key = StringField("Ключ на чтение", validators=[DataRequired()], render_kw={
        "placeholder": "4L7Vxsfw4Zjb5WRZXmbYGWzoF2sX8Ve4"
    })
    submit = SubmitField("Создать миксин")
