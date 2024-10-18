import os
import sqlite3
import sys
from dataclasses import dataclass

import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from config import config
from utils import dbhandler, queries

# Mock configuration and queries for testing
config.DB_NAME = ":memory:"  # Use in-memory database for testing


def test_handler():
    db_handler = dbhandler.DataBaseHandler()
    assert db_handler is not None


def test_get_connection():
    db_handler = dbhandler.DataBaseHandler()
    conn, c = db_handler._get_connection()
    assert conn is not None
    assert c is not None


def test_add_coins_new_user():
    db_handler = dbhandler.DataBaseHandler()
    user_id = 1
    db_handler.reset_coins(user_id)
    db_handler.add_coins(user_id, "test_user", 100)
    result = db_handler.get_coins(user_id)
    assert result[0] == 100


def test_add_coins_existing_user():
    db_handler = dbhandler.DataBaseHandler()
    user_id = 1
    db_handler.reset_coins(user_id)
    db_handler.add_coins(user_id, "test_user", 100)
    db_handler.add_coins(user_id, "test_user", 50)
    result = db_handler.get_coins(user_id)
    assert result[0] == 150


def test_reset_coins():
    db_handler = dbhandler.DataBaseHandler()
    user_id = 1
    db_handler.add_coins(user_id, "test_user", 100)
    db_handler.reset_coins(user_id)
    result = db_handler.get_coins(user_id)
    assert result[0] == 0


def test_run_query():
    db_handler = dbhandler.DataBaseHandler()
    user_id = 1
    db_handler.reset_coins(user_id)
    db_handler.run_query(queries.UPDATE_COINS, (100, user_id))
    result = db_handler.get_coins(user_id)
    assert result[0] == 100