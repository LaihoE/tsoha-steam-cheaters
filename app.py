from flask import Flask
from flask import redirect ,render_template, request
import requests
from apicalls.api_calls import get_all_data
from flask_sqlalchemy import SQLAlchemy
import os
import re
from db import *


app = Flask(__name__)


uri = os.getenv("DATABASE_URL")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = uri
db = SQLAlchemy(app)

@app.route("/")
def main():
    return render_template("form.html")


@app.route("/form")
def form():
    return render_template("form.html")


@app.route("/result", methods=["POST"])
def result():
    input_id = request.form["name"]
    data = get_all_data(input_id)
    print(data)
    insert_data(data, input_id)

    return render_template("result.html", data=data)
