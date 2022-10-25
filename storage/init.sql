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

CREATE TABLE user_types (
    type_id integer NOT NULL,
    name character varying(32),
    max_channel_count integer NOT NULL,
    max_message_size integer NOT NULL,
    bufferization boolean NOT NULL,
    max_bufferred_message_count integer NOT NULL,
    buffered_data_persistency integer NOT NULL,
    end_to_end_data_encryption boolean NOT NULL
);

INSERT INTO user_types (name,
                        max_channel_count,
                        max_message_size,
                        bufferization,
                        max_bufferred_message_count,
                        buffered_data_persistency,
                        end_to_end_data_encryption)
VALUES ('Free', 2, 256, true, 256, 12, false);