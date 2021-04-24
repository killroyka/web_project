web: python main.py
heroku ps:scale web=1
web: gunicorn --bind 0.0.0.0:$PORT flaskapp:app