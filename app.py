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

@app.route("/get_ads", methods=["GET", "POST"])
def get_ads():
    if request.method == "POST":
        approved_by = "on" if request.form.get("approved_by") else "off"
        ad = {
            "comment": request.form.get("comment"),
            "approved_by": request.form.get("approved_by"),

        }
        mongo.db.ads.insert_one(ad)
        flash("Ad added!")
        return redirect(url_for("get_ads"))

    ads = mongo.db.ads.find()
    return render_template("ads.html", ads=ads)


@app.route("/approved_ads")
def approved_ads():
    ads = mongo.db.ads.find()
    return render_template("approved_ads.html", ads=ads)

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
            "deadline": request.form.get("deadline"),
            "created_by": session["user"]
        }
        mongo.db.ads.insert_one(ad)
        flash("Ad added!")
        return redirect(url_for("get_ads"))

    adGroups = mongo.db.adGroups.find().sort("adGroup_name", 1)
    return render_template("add_ad.html", adGroups=adGroups)


@app.route("/edit_ad/<ad_id>", methods=["GET", "POST"])
def edit_ad(ad_id):

    if request.method == "POST":
        submit_ad = {
            "adGroup_name": request.form.get("adGroup_name"),
            "heading1": request.form.get("heading1"),
            "heading2": request.form.get("heading2"),
            "description": request.form.get("description"),
            "landing_page": request.form.get("landing_page"),
            "deadline": request.form.get("deadline"),
            "created_by": session["user"]
        }
        mongo.db.ads.update({"_id": ObjectId(ad_id)}, submit_ad)
        flash("Ad updated")

    ad = mongo.db.ads.find_one({"_id": ObjectId(ad_id)})
    adGroups = mongo.db.adGroups.find().sort("adGroup_name", 1)
    return render_template("edit_ad.html", ad=ad, adGroups=adGroups)


@app.route("/comment_ad/<ad_id>", methods=["GET", "POST"])
def comment_ad(ad_id):

    if request.method == "POST":
        comment_ad = {
            "adGroup_name": request.form.get("adGroup_name"),
            "heading1": request.form.get("heading1"),
            "heading2": request.form.get("heading2"),
            "description": request.form.get("description"),
            "landing_page": request.form.get("landing_page"),
            "comment": request.form.get("comment"),
            "deadline": request.form.get("deadline"),
            "created_by": session["user"]
        }
        mongo.db.ads.update({"_id": ObjectId(ad_id)}, comment_ad)
        flash("Comment updated")

    ad = mongo.db.ads.find_one({"_id": ObjectId(ad_id)})
    adGroups = mongo.db.adGroups.find().sort("adGroup_name", 1)
    return render_template("comment_ad.html", ad=ad, adGroups=adGroups)


@app.route("/delete_ad/<ad_id>")
def delete_ad(ad_id):
    mongo.db.ads.remove({"_id": ObjectId(ad_id)})
    flash("Ad deleted")
    return redirect(url_for("get_ads"))


@app.route("/adgroups")
def adgroups():
    adGroups = list(mongo.db.adGroups.find().sort("adGroup_name", 1))
    return render_template("adgroups.html", adGroups=adGroups)


@app.route("/add_adgroup", methods=["GET", "POST"])
def add_adgroup():
    if request.method == "POST":
        adgroup = {
            "adGroup_name": request.form.get("adGroup_name")
        }
        mongo.db.adGroups.insert_one(adgroup)
        flash("Ad Group added")
        return redirect(url_for("adgroups"))

    return render_template("add_adgroup.html")



@app.route("/edit_adgroup/<adgroup_id>", methods=["GET", "POST"])
def edit_adgroup(adgroup_id):
    if request.method == "POST":
        submit = {
            "adGroup_name": request.form.get("adGroup_name")
        }
        mongo.db.adGroups.update({"_id": ObjectId(adgroup_id)}, submit)
        flash("Ad group updated!")
        return redirect(url_for("adgroups"))

    adgroup = mongo.db.adGroups.find_one({"_id": ObjectId(adgroup_id)})
    return render_template("edit_adgroup.html", adgroup=adgroup)



@app.route("/delete_adgroup/<adgroup_id>")
def delete_adgroup(adgroup_id):
    mongo.db.adGroups.remove({"_id": ObjectId(adgroup_id)})
    flash("Ad Group deleted")
    return redirect(url_for("adgroups"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
