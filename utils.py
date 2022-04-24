import pandas as pd
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from flask import redirect ,render_template, request, session



app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")


uri = os.getenv("DATABASE_URL")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = uri
db = SQLAlchemy(app)



def check_input(input_id):
    try:
        input_id = int(input_id)
    except ValueError:
            return False
    if len(str(input_id)) != len('76561197991348083') or not (75000000000000000 < input_id < 77000000000000000):
        return False
    return True


def dict_to_html_df(d, single_row=False):
    if single_row:
        return pd.DataFrame.from_dict({k:[v] for k, v in d.items()})
    else:
        return pd.DataFrame.from_dict(d)


def check_register(username, password):
    if username is None or password is None:
        return [False, "Username or password is empty"]

    if len(username) > 30 or len(password) > 30:
        return [False, "Password is too long"]

    sql = "SELECT id FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if user:
       return [False, "Username already exists"] 

    return [True, "ok"]



def check_login(username, password):
    sql = "SELECT id, password FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if not user:
        return False
    else:
        hash_value = user.password
        if check_password_hash(hash_value, password):
            session["username"] = username
            return True
        else:
            return False