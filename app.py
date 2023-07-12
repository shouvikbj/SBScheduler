from flask import Flask, render_template, redirect, request, flash, make_response
import os
import json
import copy
import uuid
from gp_hashing.generateHash import generateHash

app = Flask(__name__, static_url_path="")
app.secret_key = "this is a secret key"

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/createuser", methods=["POST"])
def createuser():
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    hashed_password = generateHash(password)
    new_id = str(uuid.uuid4())
    new_user = {
        new_id: {
            "name": name,
            "email": email,
            "password": hashed_password
        }
    }
    with open(f"{APP_ROOT}/db/users.json", "r") as json_file:
        users = json.load(json_file)
        backup_users = copy.deepcopy(users)
    for id, user in users.items():
        if user["email"]==email:
            flash("Email already in use!", "warning")
            return redirect("/signup")
    else:
        users.update(new_user)
    try:
        with open(f"{APP_ROOT}/db/users.json", "w") as json_file:
            json_file.seek(0)
            json.dump(users, json_file, indent=2)
            flash("Account created!", "primary")
            return redirect("/login")
    except Exception:
        with open(f"{APP_ROOT}/db/users.json", "w") as json_file:
            json_file.seek(0)
            json.dump(backup_users, json_file, indent=2)
        flash("Account was not created!", "danger")
        return redirect("/signup")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/loginuser", methods=["POST"])
def loginuser():
    email = request.form.get("email")
    password = request.form.get("password")
    with open(f"{APP_ROOT}/db/users.json", "r") as json_file:
        users = json.load(json_file)
    for id, user in users.items():
        if user["email"]==email and user["password"]==generateHash(password):
            resp = make_response(redirect("/"))
            resp.set_cookie('user_id', id, max_age=60*60*24*365*2)
            flash("Logged in!", "primary")
            return resp
        else:
            flash("Wrong credentials!", "danger")
            return redirect("/login")

@app.route("/")
def index():
    if request.cookies.get("user_id"):
        return render_template("index.html")
    else:
        return redirect("/login")

@app.route("/view/all")
def view_all():
    if request.cookies.get("user_id"):
        with open(f"{APP_ROOT}/db/data.json", "r") as json_file:
            data = json.load(json_file)
        return render_template("viewall.html", data=data)
    else:
        return redirect("/login")

@app.route("/create/folder")
def create_folder():
    if request.cookies.get("user_id"):
        return render_template("create_folder.html")
    else:
        return redirect("/login")

@app.route("/createfolder", methods=["POST"])
def createfolder():
    foldername = request.form.get("foldername")
    folder_id = str(uuid.uuid4())
    with open(f"{APP_ROOT}/db/data.json", "r") as json_file:
        data = json.load(json_file)
        backup_data = copy.deepcopy(data)
    new_folder = {
        folder_id: {
            "name": foldername,
            "schedules": []
        }
    }
    try:
        data.update(new_folder)
        with open(f"{APP_ROOT}/db/data.json", "w") as json_file:
            json_file.seek(0)
            json.dump(data, json_file, indent=2)
        flash("Folder created!", "primary")
        return redirect(f"/folder/{folder_id}")
    except Exception:
        with open(f"{APP_ROOT}/db/data.json", "w") as json_file:
            json_file.seek(0)
            json.dump(backup_data, json_file, indent=2)
        flash("Folder was not created!", "danger")
        return redirect("/create/folder")

@app.route("/folder/<folder_id>")
def folder(folder_id):
    if request.cookies.get("user_id"):
        with open(f"{APP_ROOT}/db/data.json", "r") as json_file:
            data = json.load(json_file)
        folder = data[folder_id]
        return render_template("folder.html", folder=folder, folder_id=folder_id)
    else:
        return redirect("/login")

@app.route("/folder/<folder_id>/create", methods=["POST"])
def create_entry(folder_id):
    time = request.form.get("time")
    topic = request.form.get("topic")
    with open(f"{APP_ROOT}/db/data.json", "r") as json_file:
        data = json.load(json_file)
        backup_data = copy.deepcopy(data)
    new_entry = {
        "id": str(uuid.uuid4()),
        "time": time,
        "topic": topic
    }
    try:
        data[folder_id]["schedules"].insert(0, new_entry)
        with open(f"{APP_ROOT}/db/data.json", "w") as json_file:
            json_file.seek(0)
            json.dump(data, json_file, indent=2)
        flash("Entry created!", "primary")
        return redirect(f"/folder/{folder_id}")
    except Exception:
        with open(f"{APP_ROOT}/db/data.json", "w") as json_file:
            json_file.seek(0)
            json.dump(backup_data, json_file, indent=2)
        flash("Entry was not created!", "danger")
        return redirect(f"/folder/{folder_id}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9999, debug=True)