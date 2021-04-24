from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, IntegerField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    surname = StringField('Фамилия пользователя', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    age = IntegerField("Возраст Пользователя", validators=[DataRequired()])
    about = TextAreaField("Опиши себя(2-3 предложения)")
    submit = SubmitField('Создать')


class AddFunForm(FlaskForm):
    name = StringField("Название развлечения")
    text = TextAreaField("Описание развлечения")
    submit = SubmitField('Создать')


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class ConfirmMail(FlaskForm):
    code = IntegerField("код из сообщения на твоей почте")
    submit = SubmitField('проврить')


class CheckPsycho(FlaskForm):
    working_capacity = StringField("оцени свою работоспособность (от 0 до 10)")
    happiness = StringField("насколько ты счастлив(-а) (от 0 до 10)")
    health = StringField("Сдоров(-а) ли ты (от 0 до 10)")
    text = TextAreaField("Опиши свое состояние")
    submit = SubmitField('проврить')


