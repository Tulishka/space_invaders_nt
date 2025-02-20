## Space Invaders: "Новая угроза"

> Отслеживать ход реализации можно [здесь](docs/TZ_STATUS.md)

> Для облегчения тестирования можно воспользоваться [читами](docs/CHEATS.md)

> На github [добавлен релиз](https://github.com/Tulishka/space_invaders_nt/releases/tag/v0.9), для облегчения запуска 

### Об игре

**Space Invaders**: "Новая угроза" — это современная интерпретация легендарной аркадной игры Space Invaders, созданной в
1978 году Томохиро Нисикадо. "Новая угроза" сохраняет дух оригинала, добавляя новые элементы, чтобы сделать игровой
процесс еще более увлекательным и сложным. Вам предстоит противостоять инопланетному вторжению, используя всю свою
ловкость и реакцию, ведь в этот раз у вас нет защитных барьеров!

### Автор

Разработчик: Прийменко Ирина ([github](https://github.com/Tulishka))

### Описание игрового процесса

Игрокам предстоит защищать Землю от волн инопланетных захватчиков. Вы должны полагаться на точность и скорость, чтобы
выжить и уничтожить всех врагов. В игре доступен режим совместной игры, где два игрока могут сражаться бок о бок, чтобы
отбивать атаки врагов. Однако коварный враг адаптируется к вашему взаимодействию - сложность будет выше в режиме для
двух игроков. Кроме того, в игру добавлены новые виды врагов, включая мощного финального босса — корабль-носитель,
который станет настоящим испытанием для самых опытных игроков.

#### Цели игры

1. Уничтожить всех инопланетных захватчиков на уровне.
2. Набрать как можно больше очков.
3. Выжить в сложных волнах атак и победить финального босса.
4. Соревноваться в таблице рекордов.

### Управление

- **Игрок 1**:
    - Влево/Вправо: Стрелки влево/вправо
    - Выстрел: ctrl
- **Игрок 2**:
    - Влево/Вправо: A/D
    - Выстрел: space
- **Esc**: Внутриигровое меню.

> Подсказки по управлению можно увидеть во время игры, во внутри-игровом меню.

### Реализация

* Техническое задание находится [здесь](docs/TZ.md)
* Реализация по этапам [здесь](docs/TZ_STATUS.md)

#### Структура проекта
```
├───docs
├───img
├───music
├───result_server
├───sound
├───src
│   ├───aliens
│   ├───components
│   ├───core
│   ├───menu
│   ├───scenes
├───main.py
├───requirements.txt
├───README.md
```

### Описание классов

#### Экраны

* SceneManager - класс для переключения сцен (экранов)
* Scene - базовый класс сцены
  * MenuScene - сцена экрана меню
  * GameScene - сцена уровня
  * GameOverScene - базовый класс, сцена завершения
    * DefeatScene - сцена поражения
    * VictoryScene - сцена поражения
  * TrailerScene - сцена перед очередным уровнем
  * BossScene - сцена финальной битвы
  * ScoresScene - сцена для зала героев (таблица результатов)
  * SettingsScene - экран настроек

##### Объекты игры

* Player - класс для отображения игрока
* Swarm - реализует рой
* Alien - базовый класс пришельца из роя
  * BonusAlien - бонусный пришелец
  * BossAlien - реализует корабль-носитель
  * AcolyteAlien - пришелец-прислужник
  * MinionAlien - пришелец-миньон (выпускает корабль-носитель)
  * SceneAlien - Пришелец для анимации на экранах меню.
  * LaserArmAlien - класс для реализации выдвижной руки Дваарма.
* Projectile - базовый класс выстрела
  * Bullet - выстрел (пуля) игрока
  * Bomb - выстрел (бомба) пришельца
  * Beam - выстрел лазера Дваарма 

##### UI

* Menu - класс для реализации меню
  * MenuItem - базовый класс пункта меню
    * ImageMenuItem - пункт меню (на основе изображения)
    * MarginMenuItem - отступ (для создания промежутка между пунктами меню)
    * SwitchMenuItem - пункт меню, который можно "листать" влево/вправо выбирая значение из списка


### Технологии

* python 3.11
* pygame
* sqlite
* requests
* flask (в results_server)

### Запуск игры из исходников

* клонировать репозиторий и создать виртуальное окружение
* установить зависимости
* можно запускать

>   ```bash
>    python main.py
>  ```

### Запуск сборки

> Скачайте с github [релиз](https://github.com/Tulishka/space_invaders_nt/releases/tag/v0.9) 

> Для запуска на `macos` потребуется выполнить строку в терминале:
> 
> ```
> xattr -dr com.apple.quarantine ~/Downloads/space_invaders
> ```
> В случае если папка `space_invaders` с игрой распаковалась в папке `Загрузки`. 
> Если в другом месте - путь нужно поправить.

Приятной игры и удачи в сражениях с пришельцами!