from flask import Flask
from flask import redirect ,render_template, request
import requests
from apicalls.api_calls import *
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
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
    friends_list = get_friends_list_from_id(input_id)
    insert_friends(input_id, friends_list)
    friends = get_friends(input_id)
    return render_template("result.html", steam_hours=friends)
