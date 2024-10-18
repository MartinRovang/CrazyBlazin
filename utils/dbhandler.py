import sqlite3
from dataclasses import dataclass

from beartype import beartype
from beartype.typing import Tuple, Union

import utils.queries as queries
from config import config


@dataclass
class DataBaseHandler:
    db_name: str = config.DB_NAME

    @beartype
    def _get_connection(self) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
        """Establish and return a database connection and cursor."""
        conn = sqlite3.connect(self.db_name, check_same_thread=False)  # Thread-safe connection
        return conn, conn.cursor()

    @beartype
    def __post_init__(self) -> None:
        """Initialize the database tables."""
        conn, c = self._get_connection()
        c.execute(queries.INIT_DB_TABLE)
        conn.commit()
        conn.close()

    @beartype
    def add_coins(self, user_id: int, username: str, amount: int) -> None:
        """Add coins to a user or create a new user entry if they don't exist."""
        conn, c = self._get_connection()
        c.execute(queries.GET_COINS, (user_id,))
        result = c.fetchone()
        if result is None:
            # User not in database, add them
            c.execute(queries.ADD_COINS, (user_id, username, amount))
        else:
            # Update coins for existing user
            new_amount = result[0] + amount
            c.execute(queries.UPDATE_COINS, (new_amount, user_id))
        conn.commit()
        conn.close()

    @beartype
    def run_query(self, query: str, params: tuple) -> sqlite3.Cursor:
        """Execute a generic query with parameters and return the cursor."""
        conn, c = self._get_connection()
        c.execute(query, params)
        conn.commit()
        conn.close()
        return c

    @beartype
    def update_coins(self, user_id: int, amount: int) -> None:
        """Update the amount of coins for a specific user."""
        conn, c = self._get_connection()
        c.execute(queries.UPDATE_COINS, (amount, user_id))
        conn.commit()
        conn.close()

    @beartype
    def get_coins(self, user_id: int) -> Union[None, Tuple[int]]:
        """Retrieve the number of coins for a specific user."""
        conn, c = self._get_connection()
        c.execute(queries.GET_COINS, (user_id,))
        result = c.fetchone()
        conn.close()
        return result

    @beartype
    def reset_coins(self, user_id: int) -> None:
        """Reset the number of coins for a specific user."""
        conn, c = self._get_connection()
        c.execute(queries.RESET_COINS, (user_id,))
        conn.commit()
        conn.close()

    @beartype
    def get_top_users(self, limit: int) -> list:
        """Retrieve the top users with the most coins."""
        conn, c = self._get_connection()
        c.execute(f'SELECT * FROM users ORDER BY coins DESC LIMIT {limit}')
        result = c.fetchall()
        conn.close()
        return result
