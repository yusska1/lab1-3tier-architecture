import requests  # библиотека для отправки HTTP-запросов

BASE_URL = "http://127.0.0.1:5000"


# логин пользователя
def login():
    username = input("Username: ").strip()
    password = input("Password: ").strip()

    # отправляем POST запрос на сервер
    r = requests.post(BASE_URL + "/login", json={
        "username": username,
        "password": password
    })

    data = r.json()
    print(data)

    return data


# создание задачи
def create_task(token):
    title = input("Title: ")
    desc = input("Description: ")

    r = requests.post(
        BASE_URL + "/tasks",
        json={"title": title, "description": desc},
        headers={"Authorization": str(token)}  # передаём токен
    )

    print(r.json())


# получение задач
def get_tasks(token):
    r = requests.get(
        BASE_URL + "/tasks",
        headers={"Authorization": str(token)}
    )

    print(r.json())


# основная логика программы
data = login()

# если логин не удался
if "token" not in data:
    print("Login failed!")
    exit()

token = data["token"]

# простое меню
while True:
    print("\n1. Create task")
    print("2. Get tasks")
    print("3. Exit")

    choice = input("> ")

    if choice == "1":
        create_task(token)
    elif choice == "2":
        get_tasks(token)
    elif choice == "3":
        break
    else:
        print("Invalid choice")