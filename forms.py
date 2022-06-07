#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\


from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, \
    SubmitField, HiddenField, RadioField
from wtforms.validators import DataRequired, Length, Email


class LoginForm(FlaskForm):
    """ WTForm for logging in """
    email = StringField("Электропочта", validators=[Email()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    remember_me = BooleanField("Запомнить меня")

    submit = SubmitField("Войти")


class RegisterForm(FlaskForm):
    """ WTForm for registration """

    email = StringField("Электропочта", validators=[Email()])
    username = StringField("Ваше имя", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    password_again = PasswordField("Еще раз пароль",
                                   validators=[DataRequired()])

    submit = SubmitField("Зарегистрироваться")


class RegisterChannelForm(FlaskForm):
    """ WTForm for channel creation """

    name = StringField("Название", validators=[DataRequired()])

    submit = SubmitField("Создать канал")


class RenameChannelForm(FlaskForm):
    """ WTForm for channel name changing """

    id = HiddenField("", validators=[DataRequired()])
    name = StringField("Название", validators=[DataRequired(), Length(
        min=1, max=20, message="Не больше 20 символов")])

    submit = SubmitField("Сохранить изменения")


class CreateKeyForm(FlaskForm):
    """ WTForm for key creating """

    id = HiddenField("", validators=[DataRequired()])
    name = StringField("Название", validators=[DataRequired(), Length(
        min=1, max=20, message="Не больше 20 символов")])
    permissions = RadioField("", choices=[('0', 'Прием'),
                                          ('1', 'Отправка')],
                             default='1')
    info_allowed = BooleanField("Разрешить info", false_values=["0"])
    submit = SubmitField("Создать ключ")


class ToggleKeyActiveForm(FlaskForm):
    key = HiddenField("", validators=[DataRequired()])


class CreateMixinForm(FlaskForm):
    """ WTForm for mixin creation """

    channel = HiddenField("", validators=[DataRequired()])
    key = StringField("Ключ на чтение",
                      validators=[DataRequired()],
                      render_kw={"placeholder": "X" * 32})
    submit = SubmitField("Создать миксин")


class DeleteKeyForm(FlaskForm):
    """ WTForm for key deletion """

    key = HiddenField("", validators=[DataRequired()])
    submit = SubmitField("Удалить")


class ToggleKeyForm(FlaskForm):
    """ WTForm for key toggling """

    key = HiddenField("", validators=[DataRequired()])
    submit = SubmitField("Сменить состояние")


class ChangeUsernameForm(FlaskForm):
    """ WTForm for username changing """

    new_username = StringField("Новое имя", validators=[DataRequired()])
    submit = SubmitField("Изменить")


class ChangeEmailForm(FlaskForm):
    """ WTForm for e-mail changing """

    new_email = StringField("Новая электропочта",
                            validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    submit = SubmitField("Изменить")


class ChangePasswordForm(FlaskForm):
    """ WTForm for password changing """

    old_password = PasswordField("Старый пароль",
                                 validators=[DataRequired()])
    password = PasswordField("Новый пароль",
                             validators=[DataRequired()])
    password_again = PasswordField("Новый пароль еще раз",
                                   validators=[DataRequired()])

    submit = SubmitField("Изменить")


class RestrictMxForm(FlaskForm):
    """ WTForm for mixin restriction """

    subject = HiddenField("", validators=[DataRequired()])
    channel = HiddenField("", validators=[DataRequired()])
    mixin_type = HiddenField("", validators=[DataRequired()])

    submit = SubmitField("Удалить")
