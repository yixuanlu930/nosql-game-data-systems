CREATE KEYSPACE leaderboards WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 2};

USE leaderboards;

CREATE TABLE hall_of_fame_by_country (
    country TEXT,
    dungeon_id INT,
    time_minutes INT,
    email TEXT,
    user_name TEXT,
    date TIMESTAMP,
    dungeon_name TEXT STATIC,
    PRIMARY KEY ((country, dungeon_id), time_minutes, email)
) WITH CLUSTERING ORDER BY (time_minutes ASC, email ASC);

COPY hall_of_fame_by_country (country, dungeon_id, time_minutes, email, user_name, date, dungeon_name) FROM 'csv_tablas/hall_of_fame_by_country.csv' WITH DELIMITER = ',' AND HEADER = TRUE;

CREATE TABLE dungeons_by_country (
    country TEXT,
    dungeon_id INT,
    PRIMARY KEY ((country), dungeon_id)
) WITH CLUSTERING ORDER BY (dungeon_id ASC);

COPY dungeons_by_country (country, dungeon_id) FROM 'csv_tablas/dungeons_by_country.csv' WITH DELIMITER = ',' AND HEADER = TRUE;

CREATE TABLE user_statistics_by_dungeon (
    email TEXT,
    dungeon_id INT,
    time_minutes INT,
    date TIMESTAMP,
    PRIMARY KEY ((email, dungeon_id), time_minutes, date)
) WITH CLUSTERING ORDER BY (time_minutes ASC, date ASC);

COPY user_statistics_by_dungeon (email, dungeon_id, time_minutes, date) FROM 'csv_tablas/user_statistics_by_dungeon.csv' WITH DELIMITER = ',' AND HEADER = TRUE;


CREATE TABLE top_horde_by_event (
    country TEXT,
    event_id INT,
    n_killed INT,
    user_name TEXT,
    email TEXT,
    PRIMARY KEY ((country, event_id), n_killed, email)
) WITH CLUSTERING ORDER BY (n_killed DESC, email ASC);

-- Creamos el índice sobre la columna email para poder filtrar por ella. Necesario para la escritura de la tabla top_horde_by_event, en la tarea 6.
CREATE INDEX IF NOT EXISTS idx_email_horde ON top_horde_by_event (email);

COPY top_horde_by_event (country, event_id, n_killed, user_name, email) FROM 'csv_tablas/top_horde_by_event.csv' WITH DELIMITER = ',' AND HEADER = TRUE;