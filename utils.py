import pandas as pd
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from flask import redirect ,render_template, request, session
from app import app
from db import db




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
        return [False, "Username or password is empty."]
    
    if len(username) > 30 or len(password) > 30:
        return [False, "Username or password is too long (max 30)"]
    
    if len(username) == 0 or len(password) == 0:
        return [False, "Username or password is empty."]


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