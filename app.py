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

@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/get_ads")
def get_ads():
    ads = mongo.db.ads.find()
    return render_template("ads.html", ads=ads)

# Register function
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        existing_user = mongo.db.clients.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "company": request.form.get("company").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.clients.insert_one(register)

        session["user"] = request.form.get("username").lower()
        flash("Registraion successfull!")
        return redirect(url_for("profile", username=session["user"]))
    return render_template("register.html")

# Login function
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        existing_user = mongo.db.clients.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            if check_password_hash(
               existing_user["password"], request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome {}".format(
                        request.form.get("username")))
                    return redirect(url_for(
                        "profile", username=session["user"]))
            else:
                flash("Incorrect Username and/or Password")
                return redirect(url_for('login'))
            
        else: 
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    username = mongo.db.clients.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for('login'))


@app.route("/add_ad", methods=["GET", "POST"])
def add_ad():
    if request.method == "POST":
        ad = {
            "adGroup_name": request.form.get("adGroup_name"),
            "heading1": request.form.get("heading1"),
            "heading2": request.form.get("heading2"),
            "description": request.form.get("description"),
            "landing_page": request.form.get("landing_page"),
            "adGroup_name": request.form.get("adGroup_name"),
            "deadline": request.form.get("deadline")
        }
        mongo.db.ads.insert_one(ad)
        flash("Ad added!")
        return redirect(url_for("get_ads"))
        
    adGroups = mongo.db.adGroups.find().sort("adGroup_name", 1)
    return render_template("add_ad.html", adGroups=adGroups)

if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
