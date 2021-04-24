from flask import Flask, render_template, redirect, make_response, request, abort
from data import db_session
import datetime
from data.users import User
from data.moods import Mood
from data.interview import Interview
from data.funs import Fun
from forms.user import RegisterForm, LoginForm, AddFunForm, ConfirmMail, CheckPsycho
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from io import BytesIO
from PIL import Image
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import random
from flask_restful import reqparse, abort, Api, Resource
import RESTfulAPI

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
api = Api(app)

api.add_resource(RESTfulAPI.FunResource, '/api/funs/<int:news_id>')
api.add_resource(RESTfulAPI.FunsListResource, '/api/fun')

#    #    ###   #       #       ######  ####### #     # #    #     #
#   #      #    #       #       #     # #     #  #   #  #   #     # #
#  #       #    #       #       #     # #     #   # #   #  #     #   #
###        #    #       #       ######  #     #    #    ###     #     #
#  #       #    #       #       #   #   #     #    #    #  #    #######
#   #      #    #       #       #    #  #     #    #    #   #   #     #
#    #    ###   ####### ####### #     # #######    #    #    #  #     #
# приступим к комментированию

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

# это функция для отправки кода потдверждения почты
def send(code, email):
    msg = MIMEMultipart()
    message = f"Hello, this is your code: \n{code}"
    password = "killroykasakhabiev"
    msg['From'] = "killerbeesexy@gmail.com"
    msg['To'] = email
    msg['Subject'] = "Subscription"
    msg.attach(MIMEText(message, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com: 587')
    server.starttls()
    server.login(msg['From'], password)
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()
    print("successfully sent email to %s:" % (msg['To']))


@app.route("/get_code/<int:user_id>")
def get_code(user_id):
    global code
    # аддрес на который перенаправляет регистрация для получения кода
    # поле происходит перенаправления на ссылку потверждения
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    code = random.randint(10000, 99999)
    send(code, user.email)
    return redirect(f"/confirm/{user_id}")

# это аддрес прохождения тестирования
@app.route('/interview', methods=['GET', 'POST'])
def get_interview():
    form = CheckPsycho()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        interview = Interview(
            working_capacity=form.working_capacity.data,
            owner_id=current_user.id,
            happiness=form.happiness.data,
            health=form.health.data,
            text=form.text.data,
        )
        db_sess.add(interview)
        db_sess.commit()
        return redirect(f"/acc/{current_user.id}")
    return render_template("interview.html", form=form)

# аддрес потдверждения почты
@app.route('/confirm/<int:user_id>', methods=['GET', 'POST'])
@login_required
def confirm(user_id):
    form = ConfirmMail()
    print(form.validate_on_submit())
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if form.validate_on_submit():
        print(str(code), str(form.code.data))
        if str(code) != str(form.code.data):
            print("xnj pf [thm?????")
            return render_template("ConfirmMail.html", message="код не верный", form=form)

        user.is_confirmed = True
        db_sess.commit()
        return redirect('/')
    return render_template("ConfirmMail.html", form=form)

# аддрес показывающий основную информацию о пользователе
@app.route('/acc/<int:user_id>')
def show_my_acc(user_id):
    db_sess = db_session.create_session()
    try:
        im = Image.open(f"static/images/users_image/{user_id}.jpg")
        print(im.size[0] / im.size[1], 16 / 9)
        if im.size[0] // im.size[1] >= 16 // 9:
            size = (300, 168)
        else:
            size = (168, 300)
    except Exception:
        size = (168, 300)
    return render_template("show_my_acc.html", user_id=str(user_id), user=db_sess.query(User).get(user_id), size=size,
                           interviews=db_sess.query(Interview).filter(Interview.owner_id == user_id).all(), len=len(db_sess.query(Interview).filter(Interview.owner_id == user_id).all()))

# регистрация
@app.route('/register', methods=['GET', 'POST'])
def reqister():
    global code
    form = RegisterForm()
    print(form.validate_on_submit())
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
            about=form.about.data
        )
        user.set_password(form.password.data)
        user.tab_about()
        db_sess.add(user)
        db_sess.commit()
        f = request.files['files']
        f.save(f"static/images/users_image/{user.id}.jpg")
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(user.id)
        return redirect(f'/login')
    print("igushufghbdusfhogubd")
    return render_template('register.html', title='Регистрация', form=form)

# главная страница сайта
@app.route("/", methods=["GET", 'POST'])
def glav():
    db_sess = db_session.create_session()
    inter = db_sess.query(Interview).all()
    funs = db_sess.query(Fun).all()
    funs.sort(key=lambda i: i.likes, reverse=True)
    print(admins)
    return render_template('index.html', funs=funs, admins=admins)

# изменение пользователя
@app.route("/edituser/<int:user_id>")
def edituser(user_id):
    form = RegisterForm()

    if request.method == "GET":
        db_sess = db_session.create_session()
        fun = db_sess.query(User).filter(
            User.id == current_user.id
        ).first()
        if fun:
            form.email.data = fun.email
            form.surname.data = fun.surname
            form.name.data = fun.name
            form.age.data = fun.age
            form.about.data = fun.about
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        fun = db_sess.query(User).filter(
            User.id == current_user.id
        ).first()
        if current_user.id in admins:
            fun = db_sess.query(Fun).filter(
                Fun.id == id).first()
        if fun:
            fun.email = form.email.data
            fun.surname = form.surname.data
            fun.name = form.name.data
            fun.age = form.age.data
            fun.about = form.about.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('register.html',
                           title='Редактирование профиля',
                           form=form,
                           admins=admins
                           )

# ошибка 404
@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return "404 not found"

# изменение развлечения
@app.route('/editfun/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_funs(id):
    form = AddFunForm()
    local_admins = admins[:]
    local_admins.append(current_user.id)

    if request.method == "GET":
        db_sess = db_session.create_session()
        fun = db_sess.query(Fun).filter(
            Fun.id == id, Fun.owner_id.in_(local_admins)
        ).first()
        print(local_admins)
        print(fun)
        if current_user.id in admins:
            fun = db_sess.query(Fun).filter(
                Fun.id == id).first()
        if fun:
            form.name.data = fun.name
            form.text.data = fun.text
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        fun = db_sess.query(Fun).filter(
            Fun.id == id, Fun.owner_id.in_(local_admins)).first()
        if current_user.id in admins:
            fun = db_sess.query(Fun).filter(
                Fun.id == id).first()
        if fun:
            fun.name = form.name.data
            fun.text = form.text.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('addFun.html',
                           title='Редактирование новости',
                           form=form,
                           admins=admins
                           )

# добавление развлечения
@app.route("/addfun", methods=['GET', 'POST'])
@login_required
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

# вход в систему
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

# выход из системы
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


def main():
    global admins
    admins = [1]
    db_session.global_init("db/blogs.db")
    app.run(port=5001, host='127.0.0.1')


if __name__ == '__main__':
    main()
