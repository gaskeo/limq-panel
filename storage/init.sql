-- sozdat bazu
CREATE DATABASE limq;

-- frontent user
CREATE USER 'limq-front'@'localhost' IDENTIFIED BY 'i77dj9wobb';

-- apu user
CREATE USER 'limq-api'@'localhost' IDENTIFIED BY 'acah9bh3fn';

-- dat dostup (aces) useram
GRANT ALL PRIVILEGES ON limq.* TO 'limq-front'@'localhost';
GRANT ALL PRIVILEGES ON limq.* TO 'limq-api'@'localhost';

-- vce!

