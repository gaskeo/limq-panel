# [LiMQ](https://github.com/emmitrin/limq) panel

This is a **user account control panel**.

Another assets for LiMQ are: [LiMQ core api](https://github.com/emmitrin/limq), [LiMQ react panel](https://github.com/gaskeo/limq-front)

[Версия на русском](README.ru.md)

LiMQ is a powerful and lightweight SaaS (cloud) message broker.

![channels](assets/channels.jpg)

Users can
- register
- manage channels
- manage channels' access keys
- manage mix-ins

via this panel.

![keys](assets/keys.jpg)

## Prerequisites
To set up the panel server:

0. Create *venv* (optional)
1. Install all deps from [`requirements.txt`](requirements.txt)
2. Actualize and merge the [frontend repo](https://github.com/gaskeo/limq-front) (optional) by `python get_front.py`
3. Install and set up [Redis](https://redis.io/) 
4. Install and set up [PostgreSQL](https://www.postgresql.org/) _v14 or newer_
5. Log into `postgres` root account and run commands from [`init.sql`](storage/init.sql)
6. Set up the environment variables:

| Key | Description | Default value |
|----------|----------|-----------------------|
| `secret_key` | Flask [secret key](https://flask.palletsprojects.com/en/2.1.x/config/#SECRET_KEY) | |
| `psql_user` | DB username | `limq_front` | 
| `psql_password` | DB password |  |
| `psql_host` | PostgreSQL host | `localhost` | 
| `psql_port` |  PostgreSQL port | `5432` |
| `psql_db` | PostgreSQL database name | `limq` |
| `redis_host` | Redis host | `localhost` |
| `redis_port` | Redis port | `6379` | 
| `redis_db` | Redis database number | `3` | 
| `redis_password` | Redis access password |  |
| `redis_limit_host`| Redis host for rate limits| `localhost` |
| `redis_limit_port` | Redis port for rate limits | `6379` |
| `redis_limit_db` | Redis database number for rate limits| `4` |
| `redis_limit_password` | Redis access password for rate limits | |


6. Finally, start the service by executing `python core.py`. Default server address is `localhost:5000`

