Здравствуйте.

Инструкция чтобы посмотреть проект:

- Клонируйте репозиторий
- Пропишите команду: "pip install python-telegram-bot"
- Зарегистрируйте своего бота в Telegram:
    - Откройте @BotFather в Telegram
    - Введите команду /newbot и следуйте инструкциям.
    - Скопируйте выданный API-токен
- Узнайте свой айди
    - Найдите бота @userinfobot
    - Напишите ему /start
    - Он скинет вам id
- Создайте config.py в корне проекта
- Заполните переменные в config.py
    - BOT_TOKEN = "ваш токен бота"
    - ADMIN_ID = "ваш Telegram user_id"
- Запустите бота командой "python main.py"
- Бот запущен. Можете тестировать

Что добавил от себя и этого не было в требованиях:

- Валидация имени и номера телефона
- Логирование и обработка ошибок
- Пользовательские сообщения об ошибках
    - Если пользователь вводит некорректные данные, бот сообщает, что именно нужно исправить
- Код разделён на модули, что облегчает поддержку и развитие проекта