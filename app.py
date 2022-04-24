import os
from flask import Flask
from flask import redirect ,render_template, request, session
from apicalls.api_calls import get_api_data
from flask_sqlalchemy import SQLAlchemy
from db_fetch import fetch_from_db
from db_insert import insert_to_db
from utils import dict_to_html_df, check_input, check_register, check_login
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")


uri = os.getenv("DATABASE_URL")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = uri
db = SQLAlchemy(app)


@app.route("/")
@app.route("/form")
def form():
    return render_template("form.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", error='')
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        success = check_login(username, password)
        if success:
            session["username"] = username
            return redirect("/")
        else:
            return render_template("login.html", error="Incorrect login!")

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "GET":
        return render_template("register.html", error='')
    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        success, error = check_register(username, password)
        if success:
            hash_value = generate_password_hash(password)
            sql = "INSERT INTO users (username, password) VALUES (:username, :password)"
            db.session.execute(sql, {"username":username, "password":hash_value})
            db.session.commit()
            return redirect("/")
        else:
            return render_template("register.html", error=error)


@app.route("/register_landing", methods=["POST", "GET"])
def register_landing():
    return redirect("/register")

@app.route("/login_landing", methods=["POST", "GET"])
def login_landing():
    return redirect("/login")


@app.route("/result", methods=["POST"])
def result():
    input_id = request.form["name"]
    ok = check_input(input_id)
    if not ok:
        return redirect("/incorrect_id")
    
    #Data
    api_data = get_api_data(input_id)
    insert_to_db(api_data, input_id)
    banned_user_data, banned_friends_data, faceit_data, steam_data = fetch_from_db(input_id)

    # Combine faceit_data and steam_data
    banned_user_data.update(faceit_data)
    banned_user_data.update(steam_data)
    friends_df = dict_to_html_df(banned_friends_data[0])
    
    n_friends_total = banned_friends_data[1]
    n_friends_banned =  banned_friends_data[2]
    banned_percentage=f"{(round(n_friends_banned / n_friends_total[0][0] * 100, 2))} %"
    
    return render_template("result.html",
                        banned_percentage=banned_percentage,
                        n_friends_total=n_friends_total,
                        n_friends_banned=n_friends_banned,
                        friends_table=[friends_df.to_html(classes='data')],
                        friends_titles=friends_df.columns.values,
                        stats=banned_user_data,
                        )

@app.route("/incorrect_id")
def incorrect_id():
    return render_template("incorrect_id.html")
