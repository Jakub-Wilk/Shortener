from flask import Flask, redirect, request, render_template
from flask_pymongo import PyMongo
import string
import random
from .env import mongo_uri

app = Flask(__name__)
app.config["MONGO_URI"] = mongo_uri

mongo = PyMongo(app)

@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "GET":
        return render_template("index.j2", success = 0)
    elif request.method == "POST":
        url = request.form["url"]
        url_id = request.form["url_id"]
        if mongo.db.link_map.find_one({"url_id": url_id}) is not None:
            return render_template("index.j2", success = -1, url = url)
        if url_id == '':
            url_id = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=6))
        if url[:4] != "http":
            url = "http://" + url
        mongo.db.link_map.insert_one({"url_id": url_id, "url": url})
        return render_template("index.j2", success = 1, url_id = url_id)

@app.route("/<url_id>/")
def redirect_to(url_id):
    if url_id == "favicon.ico":
        return "none"
    url = mongo.db.link_map.find_one({"url_id": url_id})["url"]
    if url is not None:
        return redirect(url, 301)
    else:
        return render_template("404.j2", url_id=url_id), 404