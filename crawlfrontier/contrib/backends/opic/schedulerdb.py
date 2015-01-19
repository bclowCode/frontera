"""
A simple association between pages, page change rate and page value.
"""
from abc import ABCMeta, abstractmethod

import sqlite


class SchedulerDBInterface(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def clear(self):
        """Delete all contents"""
        pass

    @abstractmethod
    def add(self, page_id, page_rate, page_value):
        """Add a new association"""
        pass

    @abstractmethod
    def get(self, page_id):
        """Get (page_rate, page_value) for the given page"""
        pass

    @abstractmethod
    def set(self, page_id, page_rate, page_value):
        """Change association"""
        pass

    @abstractmethod
    def delete(self, page_id):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def iter(self):
        """An iterator over all tuples (rate, value)"""
        pass


class SQLite(sqlite.Connection, SchedulerDBInterface):
    """A SQLite implementation for the SchedulerDBInterface"""
    def __init__(self, db=None):
        super(SQLite, self).__init__(db)

        self._cursor.executescript(
            """
            CREATE TABLE IF NOT EXISTS scores (
               page_id TEXT UNIQUE,
               rate    REAL,
               value   REAL
            );
            """
        )

    def clear(self):
        self._cursor.executescript(
            """
            DELETE FROM scores;
            """
        )

    def add(self, page_id, page_rate, page_value):
        self._cursor.execute(
            """
            INSERT OR IGNORE INTO scores VALUES (?,?,?)
            """,
            (page_id, page_rate, page_value)
        )

    def get(self, page_id):
        r = self._cursor.execute(
            """
            SELECT rate, value FROM scores WHERE page_id=?
            """,
            (page_id,)
        ).fetchone()
        return r if r is not None else (None, None)

    def set(self, page_id, page_rate, page_value):
        self._cursor.execute(
            """
            UPDATE OR IGNORE scores
            SET rate=?, value=?
            WHERE page_id=?
            """,
            (page_rate, page_value, page_id)
        )

    def delete(self, page_id):
        self._cursor.execute(
            """
            DELETE FROM scores WHERE page_id=?
            """,
            (page_id,)
        )

    def iter(self):
        return sqlite.CursorIterator(
            self._connection
                .cursor()
                .execute(
                    """
                    SELECT rate, value FROM scores
                    """
                )
        )
