from collections import Counter

from flask import Flask, request, render_template

from results_server import db

app = Flask(__name__)

db.init_db()


@app.post("/space_invaders_nt/results")
def post_result():
    """Функция добавляет результат в БД, если новый счет у игрока лучше"""
    data = request.get_json()
    required_fields = ["station_uid", "user_name", "score", "achievements"]
    if not all(field in data for field in required_fields):
        return "Не все обязательные поля переданы", 400

    result = db.insert_result(data)

    return "", (200 if result else 500)


@app.get("/space_invaders_nt/top")
def get_top():
    """Функция возвращает HTML страницу 'лучшие игроки'.

    GET-параметры:
    top - максимальное количество строк в таблице результатов
    highlight - station_uid - код станции, для подсветки ее результатов

    Так же подсвечиваются результаты отправленные с машины с uid == highlight
    """
    top = request.args.get("top", default=200, type=int)
    if top <= 0:
        top = 200

    highlight = request.args.get("highlight", default="", type=str)

    results = db.get_results(top)
    name_counts = Counter(row["user_name"] for row in results)

    ranked_results = []
    for idx, result in enumerate(results, 1):
        if name_counts[result["user_name"]] > 1:
            uid = result["station_uid"][:5]
            suffix = f"[{uid}]"
        else:
            suffix = ""

        player_name = f'{result["user_name"]}{suffix}{result["achievements"]}'
        ranked_results.append({
            "position": idx,
            "player_name": player_name,
            "score": result["score"],
            "hl": result["station_uid"] == highlight,
        })

    return render_template("results.html", results=ranked_results)


if __name__ == "__main__":
    app.run()
