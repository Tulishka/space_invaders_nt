import sqlite3

DB_NAME = 'scores.db'


def create_db():
    """Создает таблицы в БД если они не созданы"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATETIME DEFAULT CURRENT_TIMESTAMP,
            players_num INTEGER NOT NULL,
            players_names TEXT NOT NULL,
            total_score INTEGER NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_names (
            player_num INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS variables (
            name TEXT PRIMARY KEY,
            value TEXT NULL
        )
    ''')

    conn.commit()
    conn.close()


def add_game_result(players_num: int, player1: tuple[str, int], player2: tuple[str, int] = ("", 0)):
    """Сохраняет результат игры в базу данных"""
    if players_num not in (1, 2):
        raise ValueError("players_num must be 1 or 2")

    # Формирование данных для сохранения
    if players_num == 1:
        players_names = player1[0]
        total_score = player1[1]
    else:
        names = sorted([player1[0], player2[0]])
        players_names = ', '.join(names)
        total_score = player1[1] + player2[1]

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO results (players_num, players_names, total_score)
            VALUES (?, ?, ?)
        ''', (players_num, players_names, total_score))
        conn.commit()
    finally:
        conn.close()


def save_player_names(names: list[str]):
    """Сохраняет или обновляет имена игроков в базе данных"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    for idx, name in enumerate(names):
        player_num = idx + 1
        cursor.execute('''
            INSERT OR REPLACE INTO player_names 
            (player_num, name) VALUES (?, ?)
        ''', (player_num, name))

    conn.commit()
    conn.close()


def load_player_names() -> list[str]:
    """Загружает сохраненные имена игроков из базы данных"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('SELECT name FROM player_names ORDER BY player_num')
    names = [row[0] for row in cursor.fetchall()]

    if len(names) < 1:
        names.append('Player1')

    if len(names) < 2:
        names.append('Player2')

    conn.close()
    return names


def get_top_results(k=10, player_num=None) -> list[tuple[str, int, int]]:
    """Возвращает топ лучших результатов с учетом фильтров"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    query = '''
        SELECT players_names, total_score, players_num
        FROM (
            SELECT 
                players_names, 
                total_score, 
                players_num,
                ROW_NUMBER() OVER (
                    PARTITION BY players_names 
                    ORDER BY total_score DESC
                ) as rn
            FROM results
            WHERE (? IS NULL OR players_num = ?)
        ) 
        WHERE rn = 1
        ORDER BY total_score DESC
        LIMIT ?
    '''

    params = (player_num, player_num, k)
    cursor.execute(query, params)
    results = [(row[0], row[1], row[2]) for row in cursor.fetchall()]

    conn.close()
    return results


def set_var(name: str, value: str):
    """Сохраняет значение переменной в БД

    :param name: имя переменной
    :param value: значение
    :return None:
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT OR REPLACE INTO variables 
        (name, value) VALUES (?, ?)
    ''', (name, value))

    conn.commit()
    conn.close()


def get_var(name) -> str:
    """Получает значение переменной из БД

    :param name: имя переменной
    :return str: возвращает значение
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('SELECT value FROM variables WHERE name = ?', (name,))
    res = cursor.fetchall()
    conn.close()
    if len(res) == 0:
        return ""

    return res[0][0]
