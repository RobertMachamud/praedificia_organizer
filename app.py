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


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # checking if username already exist in db
        user_exists = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()}
        )

        if user_exists:
            flash("Sorry, this Username is already taken")
            return redirect(url_for("register"))

        register = {
            "name": request.form.get("name").lower(),
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password")),
            "title": request.form.get("title"),
            "email": request.form.get("email"),
            "tel": request.form.get("tel"),
            "bernd": False,
            "pers_color": "#0d6efd",
            "profile_img": "chef_profile.png",
            "saved_projects": []
        }

        mongo.db.users.insert_one(register)

        # putting new user into session cookie
        session["user"] = request.form.get("username").lower()
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")



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



@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # use session user's username from db
    user = mongo.db.users.find_one(
        {"username": session["user"]}
    )

    username = user["username"]
    if session["user"]:
        return render_template("profile.html", username=username, user=user)

    return redirect(url_for("login"))



@app.route("/clicked-project/<project_id>")
def clicked_project(project_id):
    if "user" in session:
        user = mongo.db.users.find_one(
            {"username": session["user"]}
        )
        if project_id not in user["saved_projects"]:
            button_txt = "Save Project"
        else:
            button_txt = "Unsave Project"
    else:
        button_txt = "Save Project"

    project = mongo.db.projects.find_one({"_id": ObjectId(project_id)})
    return render_template(
        "clicked_project.html", project=project, button_txt=button_txt)


@app.route("/save_project/<project_id>", methods=["GET", "POST"])
def save_project(project_id):
    user = mongo.db.users.find_one(
        {"username": session["user"]}
    )
    project = mongo.db.projects.find_one({"_id": ObjectId(project_id)})

    if project_id not in user["saved_projects"]:
        mongo.db.users.update(
            {"_id": user["_id"]},
            {"$push": {"saved_projects": project_id}}
        )
        button_txt = "Unsave project"
        flash("project Saved")
    else:
        mongo.db.users.update(
            {"_id": user["_id"]},
            {"$pull": {"saved_projects": project_id}}
        )
        button_txt = "Save project"
        flash("project Unsaved")
    return render_template(
        "clicked_project.html", project=project, button_txt=button_txt)



@app.route("/saved_projects")
def saved_projects():
    saved_projects = []
    user = mongo.db.users.find_one(
        {"username": session["user"]}
    )

    for id in user["saved_projects"]:
        retrieved_saved_recipe = mongo.db.projects.find_one(
            {"_id": ObjectId(id)})
        saved_projects.append(retrieved_saved_recipe)

    return render_template("saved_projects.html", saved_projects=saved_projects)
