SELECT_DB_NAMES = '''SELECT datname FROM pg_database;'''

SELECT_TABLES_NAMES = '''SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';'''

CREATE_TABLE_ADMINS = '''CREATE TABLE admins
(id INT PRIMARY KEY NOT NULL,
username TEXT NOT NULL,
level TEXT NOT NULL);'''

CREATE_TABLE_IP = '''CREATE TABLE ip_last
(id INT PRIMARY KEY NOT NULL,
ip TEXT NOT NULL);'''

SELECT_IP = '''SELECT ip FROM ip_last where id = 1;'''

ADD_IP = '''INSERT INTO ip_last ("id", ip) VALUES (1, '{0}');'''

UPDATE_IP = '''UPDATE ip_last set ip='{0}' where "id" = 1;'''

CREATE_DB_BOT = '''CREATE DATABASE bot;'''

DROP_TABLE_BOT = '''DROP TABLE bot;'''

ADD_ADMIN = '''INSERT INTO admins ("id", username, level) VALUES ({0}, '{1}', {2});'''

DELETE_ADMIN = '''DELETE FROM admins where id = {0};'''

SELECT_ALL_ADMINS = '''SELECT * FROM admins;'''