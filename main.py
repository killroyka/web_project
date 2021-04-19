from flask import Flask, render_template, redirect, make_response, request
from data import db_session
import datetime
from data.users import User
from data.moods import Mood
from data.funs import Fun
from forms.user import RegisterForm, LoginForm, AddFunForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from io import BytesIO
from PIL import Image

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
        )
        user.set_password(form.password.data)

        db_sess.add(user)
        db_sess.commit()
        f = request.files['files']
        f.save(f"users_image/{user.id}.jpg")
        return redirect('/login')
    print("igushufghbdusfhogubd")
    return render_template('register.html', title='Регистрация', form=form)


@app.route("/", methods=["GET", 'POST'])
def glav():
    db_sess = db_session.create_session()
    funs = db_sess.query(Fun).all()
    return render_template('index.html', funs=funs)


@app.route("/addfun", methods=['GET', 'POST'])
def addfun():
    form = AddFunForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        fun = Fun(name=form.name.data,
                  text=form.text.data,
                  owner_id=current_user.id)
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


@app.route('/like/<int:fun_id>/<action>')
@login_required
def like_action(fun_id, action):
    db_sess = db_session.create_session()
    fun = db_sess.query(Fun).filter(Fun.id == fun_id).first()
    if action == "like" and str(current_user.id) not in fun.who_like.split():
        fun.likes += 1
        fun.who_like += f" {current_user.id}"
    else:
        fun.likes -= 1
        fun.who_like = fun.who_like.replace(str(current_user.id), "")
    db_sess.commit()
    print(fun.likes, fun.who_like.split())
    return redirect(request.referrer)


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


@app.route('/sample_file_upload', methods=['POST', 'GET'])
def sample_file_upload():
    if request.method == 'GET':
        return f'''<!doctype html>
                        <html lang="en">
                          <head>
                            <meta charset="utf-8">
                            <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
                             <link rel="stylesheet"
                             href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/css/bootstrap.min.css"
                             integrity="sha384-giJF6kkoqNQ00vy+HMDP7azOuL0xtbfIcaT9wjKHr8RbDVddVHyTfAAsrekwKmP1"
                             crossorigin="anonymous">
                           
                            <title>Пример загрузки файла</title>
                          </head>
                          <body>
                            <h1>Загрузим файл</h1>
                            <form method="post" enctype="multipart/form-data">
                               <div class="form-group">
                                    <label for="photo">Выберите файл</label>
                                    <input type="file" class="form-control-file" id="photo" name="file">
                                </div>
                                <button type="submit" class="btn btn-primary">Отправить</button>
                            </form>
                          </body>
                        </html>'''
    elif request.method == 'POST':
        f = request.files['file']
        f.save("test.png")
        return "Форма отправлена"


def main():
    db_session.global_init("db/blogs.db")
    app.run(port=5000, host='127.0.0.1')


if __name__ == '__main__':
    main()
