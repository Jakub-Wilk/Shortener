from flask import Flask, redirect, request, render_template, session, url_for
from flask_pymongo import PyMongo
import string
import random
from .env import mongo_uri

app = Flask(__name__)
app.config["MONGO_URI"] = mongo_uri
app.config["SECRET_KEY"] = mongo_uri

mongo = PyMongo(app)

@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "GET":
        if "success" not in session.keys():
            session["success"] = 0
            session["url"] = ""
            session["url_id"] = ""
        success = session["success"]
        url = session["url"]
        url_id = session["url_id"]
        session["success"] = 0
        session["url"] = ""
        session["url_id"] = ""
        return render_template("index.j2", success = success, url_id = url_id, url = url)
    elif request.method == "POST":
        url = request.form["url"]
        url_id = request.form["url_id"]
        if mongo.db.link_map.find_one({"url_id": url_id}) is not None:
            session["success"] = -1
            session["url"] = url
            return redirect(url_for(".index"), 303)
        if url_id == '':
            url_id = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=6))
        if url[:4] != "http":
            url = "http://" + url
        mongo.db.link_map.insert_one({"url_id": url_id, "url": url})
        session["success"] = 1
        session["url_id"] = url_id
        return redirect(url_for(".index"), 303)

@app.route("/<url_id>/")
def redirect_to(url_id):
    if url_id == "favicon.ico":
        return "none"
    url = mongo.db.link_map.find_one({"url_id": url_id})
    if url is not None:
        return redirect(url["url"], 301)
    else:
        return render_template("404.j2", url_id=url_id), 404