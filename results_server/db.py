import sqlite3
import datetime

DB_FILENAME = "space_invaders_nt.db"


def init_db():
    """Создание таблиц в БД"""
    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            station_uid TEXT,
            user_name TEXT,
            score INTEGER,
            achievements TEXT,
            timestamp DATETIME,
            PRIMARY KEY (station_uid, user_name)
        )
    """)
    conn.commit()
    conn.close()


def insert_result(data) -> bool:
    """Функция добавляет результат в БД, если у игрока уже есть результат
    он будет обновлен на новый счет если он лучше старого
    """
    station_uid = data["station_uid"]
    user_name = data["user_name"]
    score = data["score"]
    achievements = data["achievements"]
    timestamp = datetime.datetime.now().isoformat()

    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO results (station_uid, user_name, score, achievements, timestamp)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(station_uid, user_name) DO UPDATE SET
                score = excluded.score,
                achievements = excluded.achievements,
                timestamp = excluded.timestamp
            WHERE excluded.score > results.score
        """, (station_uid, user_name, score, achievements, timestamp))
        conn.commit()
    except sqlite3.Error as e:
        return False
    finally:
        conn.close()

    return True


def get_results(top: int = 200) -> list[dict]:
    """Получение лучших результатов (top)

    :param top: число, макс количество строк в результатах
    :return: возвращает поля station_uid, user_name, score, achievements
    """

    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT station_uid, user_name, score, achievements
        FROM results
        ORDER BY score DESC, timestamp
        LIMIT ?
    """, (top,))
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    conn.close()

    results = []
    for row in rows:
        results.append(dict(zip(columns, row)))

    return results
