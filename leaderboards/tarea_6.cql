-- Establecemos consistencia fuerte para el Hall of Fame (un pequeño retardo no tiene impacto porque los jugadores están a salvo en 
-- un menú)
CONSISTENCY QUORUM;

-- LECTURA: Obtener el TOP 5 de una mazmorra en un país concreto
SELECT dungeon_id, dungeon_name, time_minutes, user_name, email, date 
FROM hall_of_fame_by_country 
WHERE country = 'ES' AND dungeon_id = 101 
LIMIT 5;

-- Establecemos consistencia fuerte para las estadísticas de usuario
CONSISTENCY QUORUM;

-- LECTURA: Mostrar todos los tiempos de un usuario para una mazmorra (ordenados de menor a mayor por la clave de clustering)
SELECT time_minutes, date 
FROM user_statistics_by_dungeon 
WHERE email = 'hero@email.com' AND dungeon_id = 101;


-- ESCRITURA: Insertar un nuevo tiempo para un usuario en una mazmorra

CONSISTENCY QUORUM;

BEGIN BATCH
    -- Insertar en el Hall of Fame si es un nuevo récord 
    INSERT INTO hall_of_fame_by_country (country, dungeon_id, time_minutes, email, user_name, date, dungeon_name) 
    VALUES ('ES', 101, 12, 'player@email.com', 'Thor', '2024-05-12T10:00:00Z', 'Cueva Helada');

    -- Insertar en las estadísticas personales del usuario.
    INSERT INTO user_statistics_by_dungeon (email, dungeon_id, time_minutes, date) 
    VALUES ('player@email.com', 101, 12, '2024-05-12T10:00:00Z');
APPLY BATCH;


CONSISTENCY ONE;

BEGIN UNLOGGED BATCH
    -- Borrar el récord anterior del jugador (requiere que el backend envíe el valor antiguo)
    DELETE FROM top_horde_by_event 
    WHERE country = 'ES' AND event_id = 505 AND n_killed = 45 AND email = 'player@email.com';

    -- Insertar el nuevo récord actualizado (hay que leer el número de monstruos matados para el evento antes de insertar el nuevo récord)
    INSERT INTO top_horde_by_event (country, event_id, n_killed, user_name, email) 
    VALUES ('ES', 505, 46, 'Thor', 'player@email.com');


APPLY BATCH;
-- LECTURA: Mostrar los N jugadores que más monstruos han matado en el evento
SELECT n_killed, user_name, email
FROM top_horde_by_event 
WHERE country = 'ES' AND event_id = 500 
LIMIT 10;