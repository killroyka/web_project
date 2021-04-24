from flask import Flask, render_template, redirect, make_response, request, abort, jsonify
from data import db_session
import datetime
from data.users import User
from data.moods import Mood
from data.funs import Fun
from forms.user import RegisterForm, LoginForm, AddFunForm, ConfirmMail
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


def abort_if_fun_not_found(fun_id):
    session = db_session.create_session()
    fun = session.query(Fun).get(fun_id)
    if not fun:
        abort(404, message=f"Fun {fun_id} not found")


class FunResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', required=True)
    parser.add_argument('text', required=True)
    parser.add_argument('owner_id', required=True, type=int)

    def get(self, fun_id):
        abort_if_fun_not_found(fun_id)
        session = db_session.create_session()
        fun = session.query(Fun).get(fun_id)
        return jsonify({'news': fun.to_dict(
            only=('name', 'text', 'owner_id'))})

    def delete(self, fun_id):
        abort_if_fun_not_found(fun_id)
        session = db_session.create_session()
        fun = session.query(Fun).get(fun_id)
        session.delete(fun)
        session.commit()
        return jsonify({'success': 'OK'})
    def put(self, fun_id):
        args = self.parser.parse_args()
        session = db_session.create_session()
        fun = session.query(Fun).get(fun_id)
        fun.name = args['name']
        fun.text = args['text']
        session.commit()
class FunsListResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', required=True)
    parser.add_argument('text', required=True)
    parser.add_argument('owner_id', required=True, type=int)
    def get(self):
        session = db_session.create_session()
        funs = session.query(Fun).all()
        print(funs)
        return jsonify({'funs': [item.to_dict(
            only=('name', 'text')) for item in funs]})

    def post(self):
        args = self.parser.parse_args()
        session = db_session.create_session()
        fun = Fun(name=args['name'], text=args['text'])
        session.add(fun)
        session.commit()
