import os
from flask import Flask
from flask import redirect ,render_template, request
from apicalls.api_calls import get_api_data
from flask_sqlalchemy import SQLAlchemy
from db_fetch import fetch_from_db
from db_insert import insert_data
from utils import dict_to_html_df
from utils import check_input


app = Flask(__name__)


uri = os.getenv("DATABASE_URL")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = uri
db = SQLAlchemy(app)


@app.route("/")
@app.route("/form")
def form():
    return render_template("form.html")


@app.route("/result", methods=["POST"])
def result():
    input_id = request.form["name"]
    ok = check_input(input_id)
    print("OK", ok)
    if not ok:
        redirect("/incorrect_id")
        return
    api_data = get_api_data(input_id)
    insert_data(api_data, input_id)
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
