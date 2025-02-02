## Space Invaders: новая угроза
### Техническое задание

> Отслеживать ход реализации можно [здесь](TZ_STATUS.md)

### Общее
- Графика - 2д
- Звуки и музыка - "8бит"
  - озвучить выстрелы игрока и пришельцев, попадание в игрока и пришельцев снаряда
  - озвучить переход на следующий уровень
  - озвучить получение бонуса (поражение бонусного пришельца или выпавшего бонуса)
  - музыка для главного меню и экрана завершения


Сразу после запуска игры появляется главное меню.

### Экран: главное меню

Заголовок: "Space Invaders: новая угроза"
Пункты меню:
* 1 игрок
* 2 игрока
* таблица рекордов

Нужный пункт меню можно выбрать с помощью кнопок со стрелками вверх/вниз, подтверждая выбор кнопкой пробел или ввод, либо с помощью нажатия цифровых кнопок - соответствующих нужному пункту.

При выборе пунктов "один игрок" или "два игрока" - запускается основной экран игры с 1-го уровня.
При выборе пункта "Таблица рекордов" - запускается экран на котором отображается таблица с лучшими результатами.

### Основной экран игры

Здесь происходит основной процесс игры.
При запуске задается параметр - уровень игры и количество игроков. 

Для каждого уровня игры определены настройки:
- количество рядов и колон пришельцев в рое
- типы пришельцев в каждом ряду
- скорость снижения роя

Скорость снижения роя удваивается если игроков - 2.

Процесс игры:

- Сверху экрана выводится номер текущего уровня, оставшиеся жизни игроков, а так же их очки.
- При игре вдвоём игроки имеют общее число жизней.
- Рой начинает движение с верхней части экрана, двигается слева на право, по достижении края экрана меняет направление движения и снижается на величину равную скорости снижения роя.
- Игрок управляет истребителем, который расположен внизу экрана - может двигаться влево или вправо и стрелять вертикально вверх.
- Попадание снаряда игрока в пришельца сразу его убивает и приносит очки в зависимости от вида пришельца
- Время от времени либо случайный пришелец, либо ближайший к игроку (находящийся на нижнем уровне) стреляет вниз
- Если игрок не увернется от выстрела, то теряет одну жизнь.  
- Если все жизни потеряны игра заканчивается - переход на экран "Game over"
- Если все пришельцы уничтожены - игра переходит на следующий уровень
- Количество уровней задается константой и настройками уровней (в коде)
- Если все уровни пройдены, то переход на финальный уровень с боссом.
- Один раз за уровень в самом верху экрана (над роем) пролетает бонусный корабль пришельцев, если его сбить то игрок на время получает улучшение оружия, а так же бонусные очки
- От уровня к уровню характер и скорость движения пришельцев могут изменяться
- 3-5 видов пришельцев, представляют различную угрозу (бросают разные снаряды)
- Если нижний ряд пришельцев роя достиг уровня игрока - случится поражение истребителя за счет столкновением с пришельцем
- Из некоторых пришельцев выпадают бонусы или штрафы - если их сбить, то они активируются на некоторое время. 
- Во время игры можно нажать ESC, чтобы приостановить игру и открыть экран внутриигровое меню

### Экран "Внутриигровое меню"

Доступен во время игры (клавиша ESC)

- при открытии ставит игру на паузу
- есть опция: выйти в главное меню
- есть возможность посмотреть кнопки управления

### Экран "Game over" (поражение)
- Отображается строка "Game over"
- Отображаются набранные очки
- есть возможность указать имя игрока
- отображается таблица рекордов

### Экран "Victory" (победа)
- Отображается строка "Victory"
- Отображаются набранные очки
- есть возможность указать имя игрока
- отображается таблица рекордов

### Экран "Boss" (финальный уровень - босс)
- Экран и процесс в целом такой же как в основной игре, отличие в рое пришельцев
- Рой пришельцев представлен одним огромным кораблем (который и является источником роев пришельцев), цель - уничтожить этот корабль
- Корабль-носитель не уничтожается с одного выстрела, а имеет полоску жизни.
- Корабль-носитель, время от времени перелетает с места на место, а так же ведет стрельбу по игрокам
- После уничтожения корабля-носителя и всех пришельцев игра переходит на завершающий экран "Victory"

### Хранение таблицы результатов
- в локальной БД, сохранять результаты игр
- отправлять и получать результаты на сервер
