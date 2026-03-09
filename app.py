import os
import random
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

# app.config["MONGO_DBNAME"] = "robertmachamud_db_user:BKKedhVcReC5wjxI@cluster0.zas8qlg.mongodb.net/"
# app.config["MONGO_URI"] = "mongodb+srv://robertmachamud_db_user:BKKedhVcReC5wjxI@cluster0.zas8qlg.mongodb.net/"
# app.secret_key = "BKKedhVcReC5wjxI"



mongo = PyMongo(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # checking if username in db
        user_exists = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if user_exists:
            # checking if password is matching user input
            if check_password_hash(
                    user_exists["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                # flash()
                return redirect(url_for("profile", username=session["user"]))
            else:
                flash("Username and/or Password incorrect")
                return redirect(url_for("login"))

        else:
            # in case username doesn't exists
            flash("Username and/or Password incorrect")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    # removing user from sessions cookies
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/index")
def index():
    projects = list(mongo.db.projects.find())
    categories = list(mongo.db.categories.find())
    return render_template("index.html", projects=projects,
                    categories=categories)
