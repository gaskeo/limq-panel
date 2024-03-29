CREATE
DATABASE limq;

-- frontend user
CREATE
USER limq_front WITH ENCRYPTED PASSWORD 'i77dj9wobb';

-- api user
CREATE
USER limq_api WITH ENCRYPTED PASSWORD 'acah9bh3fn';

GRANT ALL PRIVILEGES ON DATABASE
limq TO limq_front;
GRANT ALL PRIVILEGES ON DATABASE
limq TO limq_api;

-- create buffer table for API
CREATE TABLE messages
(
    id       SERIAL,
    tag      VARCHAR(128),
    msg_type int,
    content  bytea
);