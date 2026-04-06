from flask import Flask, render_template, request, redirect, session
import sqlite3
import random

app = Flask(__name__)
app.secret_key = "secret_key"

def get_db():
    return sqlite3.connect("app.db")

# DB初期化
def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        video_url TEXT,
        item_url TEXT,
        tags TEXT,
        likes INTEGER,
        saves INTEGER
    )
    """)

    conn.commit()
    conn.close()

init_db()

# トップ
@app.route("/")
def index():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM posts")
    posts = cur.fetchall()
    conn.close()

    random.shuffle(posts)
    return render_template("index.html", posts=posts, user=session.get("user"))

# 投稿ページ
@app.route("/create")
def create():
    if "user" not in session:
        return redirect("/login")
    return render_template("create.html")

# 投稿
@app.route("/post", methods=["POST"])
def post():
    if "user" not in session:
        return redirect("/login")

    title = request.form["title"]
    video_url = request.form["video_url"]
    item_url = request.form["item_url"]
    tags = request.form["tags"]

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO posts (title, video_url, item_url, tags, likes, saves)
        VALUES (?, ?, ?, ?, 0, 0)
    """, (title, video_url, item_url, tags))
    conn.commit()
    conn.close()

    return redirect("/")

# 保存
@app.route("/save/<int:post_id>")
def save(post_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE posts SET saves = saves + 1 WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()
    return redirect("/")

# 検索
@app.route("/search")
def search():
    keyword = request.args.get("q")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM posts WHERE tags LIKE ?", ('%' + keyword + '%',))
    posts = cur.fetchall()
    conn.close()

    return render_template("index.html", posts=posts, user=session.get("user"))

# 登録
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

# ログイン
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username,password))
        user = cur.fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect("/")
        else:
            return "ログイン失敗"

    return render_template("login.html")

# ログアウト
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
