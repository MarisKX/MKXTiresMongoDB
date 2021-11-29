import os
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

mongo = PyMongo(app)


@app.route("/")
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/invoices")
def get_invoices():
    invoices = mongo.db.incoming_invoices.find()
    return render_template("invoices.html", invoices=invoices)


@app.route("/stock")
def get_stock_level():
    stock = mongo.db.stock_level.find()
    return render_template("stock.html", stock=stock)


# REGISTRATION # REGISTRATION # REGISTRATION # REGISTRATION # REGISTRATION

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists", category="info")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!", category="success")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


# LOGIN # LOGIN # LOGIN # LOGIN # LOGIN # LOGIN # LOGIN # LOGIN # LOGIN # LOGIN

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome, {}".format(
                        request.form.get("username")), category="success")
                    return redirect(url_for("profile", username=session["user"]))
            else:
                # invalid password match
                flash("Invalid Username and/or Password", category="error")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Invalid Username and/or Password", category="error")
            return redirect(url_for("login"))

    return render_template("login.html")


# PROFILE # PROFILE # PROFILE # PROFILE # PROFILE # PROFILE # PROFILE # PROFILE

@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


# LOGOUT FUNCTION # LOGOUT FUNCTION # LOGOUT FUNCTION # LOGOUT FUNCTION

@app.route("/logout")
def logout():
    # remove user from session cookie
    flash("You have been logged out", category="info")
    session.pop("user")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)