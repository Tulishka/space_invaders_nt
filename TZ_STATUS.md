### 1-й Дедлайн (13.01)
* файл с описанием [README.md](README.md)
* файл с ТЗ [TZ.md](TZ.md)

### 2-й Дедлайн (20.01)
* Заложена архитектура pygame приложения
* Сделан шаблон главного меню
* Файл настроек с описанием уровней
* Картинки пулек, пришельцев и игроков
* Звуки меню и выстрелов игрока, попадание в игрока и в пришельца
* Классы:
  * Игрока
  * Пришельцев
  * Роя пришельцев
  * Пулек и бомб
  * Игровой сцены 
  * Меню
  * Класс для переключения сцен (экранов)
* Добавлена функциональность:
  * Главное меню
  * Запуск игры для 1 игрока 
  * Запуск игры для 2 игроков
  * Перемещение игроков с помощью стрелок и кнопок (a, d) 
  * Стрельба игроков (пробел, ctrl)
  * Жизни игроков
  * Подсчёт очков
  * Попадание и смерть пришельца
  * Движение роя пришельцев по экрану (влево-вправо, вниз)
  * Сделано ускорение движения роя в зависимости от количества оставшихся пришельцев
  * Условие проигрыша если рой достигнет игроков
  * Условие проигрыша если у игроков не останется жизней
  * Условие перехода на следующий уровень (не осталось пришельцев)
  * Тестовые настройки для 3-х уровней
  * Воспроизводятся звуки в меню, стрельба игроков и попадание в игрока и пришельца
  * Звуки стрельбы пришельцев (каждый вид пришельца - свой звук выстрела)

P.s: Код будет рефакториться в дальнейшем, возможно сильно :)
