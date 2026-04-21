from flask import Flask, request, jsonify
from flasgger import Swagger
import sqlite3
import hashlib
import uuid

app = Flask(__name__)
Swagger(app)

# подключение к БД
def get_db():
    return sqlite3.connect("database.db")


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

tokens = {}

@app.route("/init")
def init_db():
    db = get_db()
    cur = db.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        role TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        owner_id INTEGER
    )
    """)

    cur.execute("DELETE FROM users")
    cur.execute("DELETE FROM tasks")

    cur.execute("INSERT INTO users VALUES (NULL, ?, ?, ?)",
                ("admin", hash_password("1234"), "admin"))

    cur.execute("INSERT INTO users VALUES (NULL, ?, ?, ?)",
                ("mod", hash_password("1234"), "moderator"))

    cur.execute("INSERT INTO users VALUES (NULL, ?, ?, ?)",
                ("user", hash_password("1234"), "viewer"))

    db.commit()
    return "DB initialized"

# логин
@app.route("/login", methods=["POST"])
def login():
    data = request.json

    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT * FROM users WHERE username=?", (data["username"],))
    user = cur.fetchone()

    if user and user[2] == hash_password(data["password"]):
        token = str(uuid.uuid4())
        tokens[token] = user

        return jsonify({
            "token": token,
            "role": user[3]
        })

    return jsonify({"error": "Invalid credentials"}), 401

def get_user(token):
    return tokens.get(token)

# получение задач
@app.route("/tasks", methods=["GET"])
def get_tasks():
    token = request.headers.get("Authorization")
    user = get_user(token)

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    db = get_db()
    cur = db.cursor()

    if user[3] == "viewer":
        cur.execute("SELECT * FROM tasks WHERE owner_id=?", (user[0],))
    else:
        cur.execute("SELECT * FROM tasks")

    return jsonify(cur.fetchall())

# создание задачи
@app.route("/tasks", methods=["POST"])
def create_task():
    token = request.headers.get("Authorization")
    user = get_user(token)

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    if user[3] not in ["admin", "moderator"]:
        return jsonify({"error": "Forbidden"}), 403

    data = request.json

    db = get_db()
    cur = db.cursor()

    cur.execute(
        "INSERT INTO tasks (title, description, owner_id) VALUES (?, ?, ?)",
        (data["title"], data["description"], user[0])
    )

    db.commit()

    return jsonify({"status": "created"})

# запуск сервера
if __name__ == "__main__":
    app.run(debug=True)