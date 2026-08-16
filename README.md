# NoSQL Game Data Systems

Authors: Yixuan Lu Guo · Shengkai Zhu   (Universidad Politécnica de Madrid-UPM)

A collection of NoSQL data systems designed for gaming applications, combining **Redis, RediSearch, semantic vector search, and Apache Cassandra**.

The project explores two different data-engineering problems:

1. A **hybrid card-search and recommendation system** built with Redis.
2. A **distributed leaderboard system** built with Apache Cassandra.

Both case studies demonstrate how NoSQL technologies can be selected and modeled according to different access patterns, scalability requirements, latency constraints, and consistency needs.

## Project Overview

The repository contains two main systems:

```text
nosql-game-data-systems/
│
├── recomendacion_cartas/
│   └── arkham_dread_data/
│       ├── arkham_dread.ipynb
│       └── cards_final_with_xp.csv
│
├── leaderboards/
│   ├── Tarea-1.ipynb
│   ├── Tarea-5.ipynb
│   ├── Tarea-6.ipynb
│   ├── leaderboards.cql
│   ├── tarea_6_rename.cql
│   ├── consultas_sql/
│   ├── csv_tablas/
│   └── Tarea_3/
│       └── docker-compose.yml
│
├── Memoria_REDIS.pdf
├── Memoria_Cassandra.pdf
└── README.md
```

---

# 1. Redis — Hybrid Card Search and Recommendation

The first part of the project implements a Redis-based cache and recommendation system for the fictional card game **Arkham Dread**.

The objective is to reduce pressure on the relational database while extending the platform with advanced search and recommendation capabilities.

## Redis Cache

Each card is stored using a Redis Hash:

```text
card:{code}
```

The implementation provides basic cache operations including:

* Check whether a card exists
* Retrieve card information
* Insert new cards
* Delete cards
* Bulk-load cards from CSV

Redis provides fast key-based access while keeping the card representation simple and flexible.

## Advanced Search with RediSearch

A RediSearch index is created to support more complex queries.

Indexed attributes include:

* Card factions
* Traits
* Experience cost
* Card name
* Card text

### Multi-Faction Search

Cards can belong to multiple factions.

The system supports:

* AND searches across several factions
* OR searches across several factions
* Multi-faction cards
* Paginated results

Faction information is represented using Redis TAG fields.

### Trait Analysis

The system can determine the most common traits associated with a faction.

RediSearch aggregation is used with operations such as:

```text
FT.AGGREGATE
GROUPBY
COUNT
```

This allows card traits to be ranked according to their frequency.

### Upgrade Search

Players can search for cards that can be used as upgrades.

The search considers:

* Card traits
* Experience cost
* Available player XP
* Preferred faction
* Exclusion of Mythos cards

Cards belonging to the player's preferred faction can receive a relevance boost while still allowing useful cards from other factions to appear.

---

# Recommendation System

Three recommendation strategies are implemented.

## Metadata-Based Recommendation

Cards are recommended according to shared structured attributes such as:

* Faction
* Traits

This provides a simple content-based recommendation baseline.

## Full-Text Recommendation

The system uses the card's:

* Name
* Description
* Text

to retrieve cards with similar textual content.

## Semantic Recommendation

The most advanced recommendation method uses sentence embeddings generated with:

```text
all-MiniLM-L6-v2
```

Each card is represented by a **384-dimensional embedding**.

The vectors are stored in Redis and searched using **K-Nearest Neighbors (KNN)**.

The resulting pipeline is conceptually:

```text
Card text
    ↓
Sentence Transformer
    ↓
384-dimensional embedding
    ↓
Redis vector index
    ↓
KNN similarity search
    ↓
Recommended cards
```

This allows cards to be recommended according to semantic similarity rather than relying only on exact words or manually defined metadata.

## Redis Technologies

* Redis 7
* RediSearch
* Redis Hashes
* Vector Search
* KNN
* Python
* redis-py
* Pandas
* NumPy
* Sentence Transformers
* PyTorch

---

# 2. Cassandra — Distributed Leaderboard System

The second part of the project implements a distributed leaderboard backend for the fictional multiplayer game **Jotun's Lair**.

Apache Cassandra is used to support high-throughput leaderboard queries and updates.

The database is designed around the application's access patterns rather than normalized relational modeling.

## Leaderboards

Three main use cases are implemented.

### Hall of Fame

Returns the fastest players for a dungeon within a particular country.

The main Cassandra partition is based on:

```text
(country, dungeon_id)
```

Results are clustered by completion time so that the best records can be retrieved efficiently.

The table is modeled as:

```sql
CREATE TABLE hall_of_fame_by_country (
    country TEXT,
    dungeon_id INT,
    time_minutes FLOAT,
    email TEXT,
    user_name TEXT,
    date TIMESTAMP,
    dungeon_name TEXT STATIC,
    PRIMARY KEY ((country, dungeon_id), time_minutes, date, email)
);
```

---

### User Statistics

Stores the historical completion times of an individual player for a specific dungeon.

The partition key is:

```text
(email, dungeon_id)
```

allowing all attempts for one player and dungeon to be retrieved directly.

---

### Top Horde

Provides a real-time ranking of players participating in a Horde event.

The partition key combines:

```text
(country, event_id)
```

while player kill counts are stored as clustering values in descending order.

This allows queries such as a Top-K leaderboard to return already ordered data without requiring expensive sorting.

---

# Query-Driven Data Modeling

The Cassandra schema is deliberately denormalized.

Instead of using joins, information required by each query is stored directly in the corresponding table.

Examples include:

* `user_name`
* `country`
* `dungeon_name`

This design reduces additional database lookups and follows Cassandra's query-first modeling philosophy.

## Cassandra Tables

The project defines tables including:

```text
hall_of_fame_by_country
dungeons_by_country
user_statistics_by_dungeon
top_horde_by_event
```

## Consistency

Different consistency requirements are considered according to the use case.

For leaderboard queries where accuracy is important, stronger consistency levels can be used.

For highly dynamic Horde rankings, lower-latency operations can be prioritized because temporary small inconsistencies are acceptable.

The project explores Cassandra consistency settings including:

```text
QUORUM
ONE
```

---

# Cassandra Cluster

A local distributed Cassandra cluster is deployed with Docker Compose.

The configuration contains **three Cassandra nodes**:

```text
cassandra-n1
cassandra-n2
cassandra-n3
```

All nodes belong to the same datacenter and rack.

The keyspace uses a replication factor of:

```text
RF = 2
```

A dedicated initialization container automatically executes the CQL schema once the Cassandra nodes become healthy.

## Starting the Cassandra Cluster

Navigate to:

```bash
cd leaderboards/Tarea_3
```

Start the cluster:

```bash
docker compose up -d
```

Check the containers:

```bash
docker compose ps
```

The Cassandra native protocol is exposed through:

```text
localhost:9042
```

Stop the cluster with:

```bash
docker compose down
```

---

# Data Import

Relational data is transformed into CSV files corresponding to the Cassandra query model.

SQL queries used for data extraction are available in:

```text
leaderboards/consultas_sql/
```

Generated datasets are stored in:

```text
leaderboards/csv_tablas/
```

The `leaderboards.cql` script creates the schema and imports the corresponding CSV files.

---

# Technologies

## Databases

* Redis
* RediSearch
* Apache Cassandra
* CQL
* SQL

## Data & Machine Learning

* Python
* Pandas
* NumPy
* Sentence Transformers
* PyTorch
* Vector embeddings
* KNN similarity search

## Infrastructure

* Docker
* Docker Compose
* Distributed database clusters

## Development

* Jupyter Notebook
* redis-py
* cassandra-driver

---

# Key Concepts

This project explores several database and distributed-systems concepts:

* NoSQL databases
* Key-value databases
* Distributed wide-column stores
* Caching
* Query-driven data modeling
* Database denormalization
* Partition keys
* Clustering columns
* Replication
* Consistency levels
* Distributed database clusters
* Full-text search
* Search indexes
* Aggregations
* Semantic search
* Vector databases
* Embeddings
* K-Nearest Neighbors
* Recommendation systems

---

# Installation

## Redis Project

Install the Python dependencies:

```bash
pip install redis pandas sentence-transformers numpy torch
```

A Redis instance with RediSearch support is required.

Then open:

```bash
jupyter notebook recomendacion_cartas/arkham_dread_data/arkham_dread.ipynb
```

## Cassandra Project

Start the Cassandra cluster:

```bash
cd leaderboards/Tarea_3
docker compose up -d
```

Install the Python dependencies:

```bash
pip install cassandra-driver pandas
```

The implementation and experiments can then be explored through the Jupyter notebooks in:

```text
leaderboards/
```

---

# Academic Context

This repository was developed as part of the **Databases II** coursework in the Bachelor's Degree in Data Science and Artificial Intelligence at Universidad Politécnica de Madrid (UPM).

The objective was to study the design and implementation of NoSQL systems using different database paradigms and to understand how data models should be adapted to specific application requirements.

---

# Disclaimer

The applications, games, and scenarios represented in this repository are used for educational purposes.

The project focuses on database architecture, distributed systems, search, and recommendation techniques rather than production deployment.

---

# License

This project is distributed under the license included in the repository.





# Spanish translation:

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
