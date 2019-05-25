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

    if request.method == "GET":
        return render_template("board/list.html", posts=posts, liked_posts=liked_posts_int)
    else:
        db = get_db()

        if request.form["post_id"] in liked_posts_str:
            del liked_posts_str[request.form["post_id"]]
            db.execute("UPDATE post SET likes = likes -1 WHERE id= ? ", request.form["post_id"])
        else:
            liked_posts_str[request.form["post_id"]] = request.form["post_id"]
            db.execute("UPDATE post SET likes = likes +1 WHERE id= ? ", request.form["post_id"])

        liked_posts_int = []
        for id in liked_posts_str:
            liked_posts_int.append(int(id))

        posts = db.execute("SELECT * FROM post ORDER BY created DESC").fetchall()
        db.commit()

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
        db.execute("INSERT INTO post (title, description, color, likes) VALUES (?,?,?,0)", (title, desc, color))
        db.commit()

        resp = make_response(redirect(url_for("board.list")))

        return resp
