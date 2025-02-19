from psycopg2 import pool, extras
from itertools import repeat, chain
from pathlib import Path
import jsonlines
import json
import os

connection_pool = pool.SimpleConnectionPool(1, 10, os.getenv("DB_DSN"))

conn = connection_pool.getconn()
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS participants")
cur.execute(
    """
CREATE TABLE participants (
  competition_id TEXT,
  teams VARCHAR[]
)
"""
)


def loaderFn(path):
    try:
        with path.open() as handle:
            return (path, json.load(handle))
    except:
        return None


for path, competition in filter(
    None, map(loaderFn, sorted(Path("data/participants").glob("*.json")))
):
    print(path)
    data = list(
        map(
            lambda teams, competition_id: (competition_id, teams),
            competition["teams"],
            repeat(competition["competition_id"]),
        )
    )
    extras.execute_values(cur, "INSERT INTO participants VALUES %s", data)

cur.execute("DROP TABLE IF EXISTS results")
cur.execute(
    """
CREATE TABLE results (
  competition_id TEXT,
  duration TEXT,
  type TEXT,
  names VARCHAR[],
  ranks JSON
)
"""
)


def computeRank(record):
    def mapper(item):
        (type, rank) = item
        return [{"type": type, "rank": rank, "label": record.get(type)}]

    return list(chain.from_iterable(map(mapper, record.get("rank", {}).items())))


for path in sorted(
    filter(lambda path: path.stat().st_size > 1, Path("data/results").glob("*.jsonl"))
):
    print(path)
    with jsonlines.open(path.resolve()) as reader:
        data = list(
            map(
                lambda record: (
                    record["competition_id"],
                    record["duration"],
                    record["type"],
                    record["names"],
                    json.dumps(computeRank(record)),
                ),
                reader,
            )
        )
        extras.execute_values(cur, "INSERT INTO results VALUES %s", data)

conn.commit()

cur.close()
connection_pool.closeall()
