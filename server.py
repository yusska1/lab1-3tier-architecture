from flask import Flask, request, jsonify  # Flask — для создания сервера
import sqlite3  # работа с базой данных SQLite
import hashlib  # для хеширования паролей

# создаём приложение Flask
app = Flask(__name__)


# подключение к базе данных
def get_db():
    # если файла database.db нет — он создастся автоматически
    return sqlite3.connect("database.db")


# функция для "шифрования" пароля
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ---------------------------
# ИНИЦИАЛИЗАЦИЯ БАЗЫ
# ---------------------------
@app.route("/init")
def init_db():
    db = get_db()
    cursor = db.cursor()

    # создаём таблицу пользователей
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        role TEXT
    )
    """)

    # создаём таблицу задач
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        owner_id INTEGER
    )
    """)

    # очищаем таблицы (чтобы каждый раз начинать с чистой базы)
    cursor.execute("DELETE FROM users")
    cursor.execute("DELETE FROM tasks")

    # добавляем тестовых пользователей
    cursor.execute("INSERT INTO users VALUES (NULL, ?, ?, ?)",
                   ("admin", hash_password("1234"), "admin"))

    cursor.execute("INSERT INTO users VALUES (NULL, ?, ?, ?)",
                   ("mod", hash_password("1234"), "moderator"))

    cursor.execute("INSERT INTO users VALUES (NULL, ?, ?, ?)",
                   ("user", hash_password("1234"), "viewer"))

    db.commit()

    return "DB initialized"


# ---------------------------
# ЛОГИН
# ---------------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json  # получаем JSON от клиента

    db = get_db()
    cursor = db.cursor()

    # ищем пользователя по имени
    cursor.execute("SELECT * FROM users WHERE username=?", (data["username"],))
    user = cursor.fetchone()

    # проверяем пароль
    if user and user[2] == hash_password(data["password"]):
        return jsonify({
            "token": user[0],  # используем id как токен
            "role": user[3]
        })

    return jsonify({"error": "Invalid credentials"}), 401


# ---------------------------
# ПОЛУЧИТЬ ЗАДАЧИ
# ---------------------------
@app.route("/tasks", methods=["GET"])
def get_tasks():
    token = request.headers.get("Authorization")  # берём токен

    db = get_db()
    cursor = db.cursor()

    # проверяем пользователя
    cursor.execute("SELECT role FROM users WHERE id=?", (token,))
    user = cursor.fetchone()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    # получаем список задач
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()

    return jsonify(tasks)


# ---------------------------
# СОЗДАТЬ ЗАДАЧУ
# ---------------------------
@app.route("/tasks", methods=["POST"])
def create_task():
    token = request.headers.get("Authorization")

    db = get_db()
    cursor = db.cursor()

    # проверяем пользователя
    cursor.execute("SELECT role FROM users WHERE id=?", (token,))
    user = cursor.fetchone()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    # проверка роли (viewer нельзя создавать задачи)
    if user[0] not in ["admin", "moderator"]:
        return jsonify({"error": "Forbidden"}), 403

    data = request.json

    # добавляем задачу в базу
    cursor.execute(
        "INSERT INTO tasks (title, description, owner_id) VALUES (?, ?, ?)",
        (data["title"], data["description"], token)
    )

    db.commit()

    return jsonify({"status": "created"})


# запуск сервера
if __name__ == "__main__":
    app.run(debug=True)