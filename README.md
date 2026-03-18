Bases de Datos II — Prácticas NoSQL

Repositorio con las prácticas de la asignatura Bases de Datos II de la Universidad Politécnica de Madrid (UPM).

Autores: Yixuan Lu Guo · Shengkai Zhu


================================================================================
Práctica 1: Redis — Búsqueda Híbrida de Cartas
================================================================================

Diseño de una caché Redis con capacidades de búsqueda avanzada para el portal web del juego de cartas "Arkham Dread" de Norsewind Studios.

Contexto

El portal web del juego necesita aliviar la carga de su base de datos SQL almacenando la información de las cartas en una caché Redis, y además extender la funcionalidad con búsquedas avanzadas y un recomendador de cartas.

Objetivos implementados

  Objetivo I — Caché básica
    - Estructura de datos: Redis Hashes (card:{code})
    - Carga masiva desde CSV
    - Operaciones CRUD: existencia, lectura, inserción y eliminación por código

  Objetivo II — Búsquedas avanzadas con RediSearch
    - A. Búsqueda por facciones (AND / OR) con soporte para cartas multifacción
    - B. Traits más comunes por facción usando FT.AGGREGATE con GROUPBY / COUNT
    - C. Búsqueda de upgrades: filtrado por xp, exclusión de mythos, boost por facción preferida

  Objetivo III — Recomendador de cartas
    - A. Recomendación por metadatos (facción + traits compartidos)
    - B. Recomendación full-text (búsqueda por palabras del nombre y texto)
    - C. Recomendación semántica (embeddings con all-MiniLM-L6-v2 + KNN vectorial)

Contenido

  arkham_dread.ipynb         Notebook completo con los tres objetivos implementados y análisis comparativo.
  cards_final_with_xp.csv    Dataset de cartas del juego.

Tecnologías

  - Redis 7.x con módulo RediSearch
  - Python (redis-py, pandas, sentence-transformers, numpy, torch)
  - Modelo de embeddings: all-MiniLM-L6-v2 (384 dimensiones)


================================================================================
Práctica 2: Cassandra — Sistema de Rankings
================================================================================

Diseño e implementación de una base de datos Apache Cassandra para dar servicio a los leaderboards del videojuego "Jotun's Lair" de Norsewind Studios.

Contexto

El juego dispone de tres leaderboards que la base de datos relacional existente no puede servir con el rendimiento necesario:

  - Hall of Fame: TOP 5 jugadores más rápidos por mazmorra y país.
  - User Statistics: Historial de tiempos de un jugador en una mazmorra.
  - Top Horde: TOP K jugadores con más kills durante un evento de Horda en tiempo real.

Contenido

  Tarea-1.ipynb              Diseño de tablas Cassandra con justificación de partition keys, clustering columns y denormalización.
  *.sql                      Consultas SQL para exportar datos de la BD relacional a CSV.
  csv_tablas/                Ficheros CSV generados para la carga inicial.
  docker-compose.yml         Clúster local de 3 nodos Cassandra (mismo datacenter y rack).
  leaderboards.cql           Creación del keyspace (SimpleStrategy, RF=2), tablas e importación de datos.
  Tarea-5.ipynb              Actualización de las escrituras del juego para el modelo denormalizado.
  tarea_6.cql                Consultas de lectura/escritura con niveles de consistencia (QUORUM / ONE).
  Tarea-6.ipynb              Implementación en Python de las lecturas y escrituras con cassandra-driver.

Tecnologías

  - Apache Cassandra 4.x
  - Docker / Docker Compose
  - Python (cassandra-driver, pandas)
  - CQL


================================================================================
Requisitos
================================================================================

Redis:
  pip install redis pandas sentence-transformers numpy torch

Cassandra:
  docker compose up -d
  pip install cassandra-driver pandas