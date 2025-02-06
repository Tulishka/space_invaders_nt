"""
В файле находятся функции для работы с API сервера результатов.
"""
import os.path
import uuid
import webbrowser
from threading import Thread

import requests

# уникальный номер станции, генерируется как uuid()
station_uid = None
SERVER_URL = "https://tulishka.pythonanywhere.com/space_invaders_nt"


def create_station_uid():
    """Создает и записывает в файл новый uid текущей станции"""
    global station_uid

    station_uid = str(uuid.uuid4())

    with open("station", "w") as file:
        file.write(station_uid)

    return station_uid


def get_station_uid():
    """Получает station_uid, создает его при необходимости"""
    if not os.path.exists("station"):
        return create_station_uid()

    global station_uid
    if station_uid:
        return station_uid
    try:
        with open("station", "r") as file:
            station_uid = file.readline().strip()
            return station_uid
    except:
        return "unknown"


def open_world_records():
    """Открывает в браузере страницу с лучшими игроками.
    Передает station_id, для подсветки в таблице "ваших" результатов.
    """
    webbrowser.open(
        f"{SERVER_URL}/top?highlight={get_station_uid()}",
        new=0, autoraise=True
    )


def send_request(data):
    """Отправка POST запроса для добавления нового результат игры.
    Результат будет добавлен сервером, только если он лучше предыдущего.
    """
    try:
        requests.post(f"{SERVER_URL}/results", json=data, headers={'Content-Type': 'application/json'})
    except Exception as e:
        print(e)


def send_world_record(player_name, score, achievements=""):
    """Подготовка и отправка в отдельном потоке запроса на добавление результата"""
    data = {
        "station_uid": get_station_uid(),
        "user_name": player_name,
        "score": score,
        "achievements": achievements,
    }
    thread = Thread(target=send_request, args=(data,))
    thread.start()
