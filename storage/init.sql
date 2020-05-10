CREATE DATABASE limq;

-- frontend user
CREATE USER 'limq-front'@'localhost' IDENTIFIED BY 'i77dj9wobb';

-- api user
CREATE USER 'limq-api'@'localhost' IDENTIFIED BY 'acah9bh3fn';

GRANT ALL PRIVILEGES ON limq.* TO 'limq-front'@'localhost';
GRANT ALL PRIVILEGES ON limq.* TO 'limq-api'@'localhost';


