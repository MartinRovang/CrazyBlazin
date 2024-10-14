CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    coins INTEGER DEFAULT 0,
    weapon TEXT DEFAULT '',
    health INTEGER DEFAULT 100
)