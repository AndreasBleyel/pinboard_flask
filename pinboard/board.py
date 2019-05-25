from flask import Blueprint, render_template, request, redirect, url_for, make_response
from pinboard.db import get_db
import json

bp = Blueprint("board", __name__)


@bp.route("/", methods=("GET", "POST"))
def list():
    db = get_db()
    posts = db.execute("SELECT * FROM post ORDER BY created DESC").fetchall()

    liked_posts_str = {}

    if request.cookies.get("ids"):
        liked_posts_str = json.loads(request.cookies.get("ids"))

    liked_posts_int = []
    for id in liked_posts_str:
        liked_posts_int.append(int(id))

    for post in posts:
        print(post["id"])
        if post["id"] in liked_posts_int:
            print("yes")
        else:
            print("no")

    # get cookie
    # check which entrys have already a like
    # disable button

    if request.method == "GET":
        return render_template("board/list.html", posts=posts, liked_posts=liked_posts_int)
    else:
        # get id from liked post
        # add id to cookies
        # redirect to "/"

        liked_posts_str[request.form["post_id"]] = request.form["post_id"]
        liked_posts_int = []
        for id in liked_posts_str:
            liked_posts_int.append(int(id))

        resp = make_response(render_template("board/list.html", posts=posts, liked_posts=liked_posts_int))
        resp.set_cookie("ids", json.dumps(liked_posts_str))
        return resp


@bp.route("/add", methods=("GET", "POST"))
def add():
    if request.method == "GET":
        return render_template("board/add.html")
    else:
        title = request.form["title"]
        desc = request.form["description"]
        color = request.form["color"]

        db = get_db()
        db.execute("INSERT INTO post (title, description, color) VALUES (?,?,?)", (title, desc, color))
        db.commit()
        post_id = db.cursor().lastrowid

        resp = make_response(redirect(url_for("board.list")))

        return resp
