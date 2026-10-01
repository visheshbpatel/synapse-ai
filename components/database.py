import sqlite3
from pathlib import Path

DATABASE_PATH = "data/synapse.db"


def get_connection():
    Path(DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DATABASE_PATH)

    