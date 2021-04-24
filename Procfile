web: python __init__.py
heroku ps:scale web=1
web: gunicorn --bind 0.0.0.0:$PORT flaskapp:app