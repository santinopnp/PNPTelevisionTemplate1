CREATE TABLE IF NOT EXISTS subscribers (
    user_id BIGINT PRIMARY KEY,
    plan TEXT NOT NULL,
    start_date TIMESTAMP NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    transaction_id TEXT
);
CREATE INDEX IF NOT EXISTS idx_subscribers_expires_at ON subscribers (expires_at);

CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    language TEXT,
    last_seen TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_users_language ON users (language);
