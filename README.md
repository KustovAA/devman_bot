### О проекте
Телеграм-бот для получения уведомлений о проверке уроков на [DEVMAN](https://dvmn.org/)

### Как установить
* ```python -m pip install pipenv (если не установлен pipenv)```
* ```pipenv shell```
* ```pipenv install```

### Как запускать
Необходиом создать телеграмм бота. <br>
Необходимо создать файл .env в корне проекта. <br>
В файле должны быть настройки:
* ```DEVMAN_ACCESS_TOKEN``` - токен к апи DEVMAN
* ```TG_BOT_TOKEN``` - токен вашего бота в телеграмм
* ```TG_USER_CHAT_ID``` - chat_id пользователя телеграма, которому нужно отправлять уведомления

Команда для запуска:

* ```python main.py```

Запуск с помощью docker:

* ```docker build -t devman-bot .``` - build docker образа
* ```docker run --env-file .env devman-bot``` - start docker контейнера