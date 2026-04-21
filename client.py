import requests

BASE_URL = "http://127.0.0.1:5000"

# логин
def login():
    username = input("Username: ")
    password = input("Password: ")

    r = requests.post(BASE_URL + "/login", json={
        "username": username,
        "password": password
    })

    return r.json()

# получение задач
def get_tasks(token):
    r = requests.get(
        BASE_URL + "/tasks",
        headers={"Authorization": token}
    )
    print(r.json())

# создание задачи
def create_task(token):
    title = input("Title: ")
    desc = input("Description: ")

    r = requests.post(
        BASE_URL + "/tasks",
        json={"title": title, "description": desc},
        headers={"Authorization": token}
    )

    print(r.json())

# запуск клиента
data = login()

if "token" not in data:
    print("Login failed")
    exit()

token = data["token"]

while True:
    print("\n1. Get tasks")
    print("2. Create task")
    print("3. Exit")

    c = input("> ")

    if c == "1":
        get_tasks(token)
    elif c == "2":
        create_task(token)
    elif c == "3":
        break