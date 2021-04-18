# from flask import Flask, render_template, redirect
# from data import db_session
# import datetime
# from data.db_session import global_init, create_session
# from data.users import User
# from data.jobs import Jobs
# from forms.user import RegisterForm

global_init(input())
db_sess = create_session()
for user in db_sess.query(User).filter(User.address.like("%1%"), User.age >= 21):
    user.addres = "module_3"
