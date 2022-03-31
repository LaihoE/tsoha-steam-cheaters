from flask import Flask
from flask import redirect ,render_template, request
import requests
from apicalls.api_calls import get_all_data
from flask_sqlalchemy import SQLAlchemy
import os
import re

app = Flask(__name__)


uri = os.getenv("DATABASE_URL")  # or other relevant config var
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = uri
db = SQLAlchemy(app)


@app.route("/form")
def form():
    return render_template("form.html")


def insert_friends(input_id, friends_list):
    for friend in friends_list:
        sql = "INSERT INTO FRIENDS (user1, user2) VALUES (:user1, :user2)"
        db.session.execute(sql, {"user1": input_id, "user2":friend})
    db.session.commit()


def get_friends(steamid):
    sql = "SELECT user2 FROM friends WHERE user1 = (:steamid)"
    result = db.session.execute(sql, {"steamid": steamid})
    out = result.fetchall()
    print(out)
    return out


@app.route("/result", methods=["POST"])
def result():
    input_id = request.form["name"]
    data = get_all_data(input_id)
    data = [[k, v] for k,v in data.items()]
    return render_template("result.html", data=data, len=len(data))
