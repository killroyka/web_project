from flask import Flask, render_template, redirect, make_response, request
from data import db_session
import datetime
from data.users import User
from data.moods import Mood
from data.funs import Fun
from forms.user import RegisterForm, LoginForm, AddFunForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/myacc')
def show_my_acc():
    return render_template("show_my_acc.html")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            age=form.age.data,
            email=form.email.data,
            password=form.password.data
        )
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    print("igushufghbdusfhogubd")
    return render_template('register.html', title='Регистрация', form=form)


@app.route("/", methods=["GET", 'POST'])
def glav():
    db_sess = db_session.create_session()
    funs = db_sess.query(Fun).all()
    return render_template('index.html',funs=funs)
@app.route("/addfun", methods=['GET', 'POST'])
def addfun():
    form = AddFunForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        fun = Fun(name=form.name.data,
                  text=form.text.data)
        db_sess.add(fun)
        db_sess.commit()
        return redirect('/')
    return render_template("addFun.html", form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def add_user(name, surname, age, position, speciality, address, email):
    db_sess = db_session.create_session()
    user = User()
    user.surname = surname
    user.name = name
    user.age = age
    user.position = position
    user.speciality = speciality
    user.address = address
    user.email = email
    db_sess.add(user)
    db_sess.commit()


def main():
    db_session.global_init("db/blogs.db")
    app.run(port=5000, host='127.0.0.1')


if __name__ == '__main__':
    main()
