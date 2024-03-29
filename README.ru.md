# Панель [LiMQ](https://github.com/emmitrin/limq)

Другие ресурсы LiMQ: [LiMQ core api](https://github.com/emmitrin/limq), [LiMQ react panel](https://github.com/gaskeo/limq-panel)

[English version](README.md)

LiMQ - эффективный облачный брокер сообщений (SaaS).

![channels](assets/channels.jpg)

С помощью данной панели можно осуществлять следующие действия:
* Регистрироваться в системе
* Управлять каналами
* Создавать ключи
* Управлять миксинами

![keys](assets/keys.jpg)
## Установка
Для работы панели необходимо: 
1. Установить все зависимости из [`requirements.txt`](requirements.txt)
2. Запустить скрипт [`get_front.py`](get_front.py), который соберет все данные с [react сервера](https://github.com/gaskeo/limq-front)
3. Установить [Redis](https://redis.io/) 
4. Установить [PostgreSQL](https://www.postgresql.org/)
5. Выполнить команды из файла [`init.sql`](storage/init.sql) 
   внутри [терминала](https://www.postgresql.org/docs/current/app-psql.html) PostgreSQL
6. Настроить переменные окружения:

| Название | Описание | Значение по умолчанию |
|----------|----------|-----------------------|
| `secret_key` | Flask [secret key](https://flask.palletsprojects.com/en/2.1.x/config/#SECRET_KEY) | |
| `psql_user` | Имя пользователя PostgreSQL | `limq_front` | 
| `psql_password` | Пароль пользователя PostgreSQL |  |
| `psql_host` | Адрес сервера PostgreSQL | `localhost` | 
| `psql_port` |  Порт сервера PostgreSQL | `5432` |
| `psql_db` | Название базы данных PostgreSQL | `limq` |
| `redis_host` | Адрес сервера redis | `localhost` |
| `redis_port` | Порт сервера redis | `6379` | 
| `redis_db` | id базы данных redis | `3` | 
| `redis_password` | Пароль redis | | 
| `redis_limit_host`| Адрес сервера redis для rate-лимитов | `localhost` |
| `redis_limit_port` | Порт сервера redis для rate-лимитов | `6379` |
| `redis_limit_db` | id базы данных redis для rate-лимитов| `4` |
| `redis_limit_password` | Пароль сервера redis для rate-лимитов | |


6. Запустить [`core.py`](core.py), сервер будет использовать `5000` порт

