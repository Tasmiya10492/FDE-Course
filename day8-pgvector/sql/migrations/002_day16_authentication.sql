-- Day 16: authentication, server-side sessions, audit and ownership.

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'employee'
        CHECK (role IN ('employee', 'line_manager', 'hr_administrator')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    password_changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email_lower
    ON users (LOWER(email));

CREATE TABLE IF NOT EXISTS user_sessions (
    session_id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id
    ON user_sessions (user_id);

CREATE INDEX IF NOT EXISTS idx_user_sessions_expiry
    ON user_sessions (expires_at);

CREATE TABLE IF NOT EXISTS login_attempts (
    email TEXT NOT NULL,
    ip_address TEXT NOT NULL,
    failed_attempts INTEGER NOT NULL DEFAULT 0,
    window_started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    locked_until TIMESTAMPTZ,
    PRIMARY KEY (email, ip_address)
);

CREATE TABLE IF NOT EXISTS audit_events (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    actor_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    event_type TEXT NOT NULL,
    target_type TEXT,
    target_id TEXT,
    ip_address TEXT,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_events_actor
    ON audit_events (actor_user_id, created_at DESC);

CREATE TABLE IF NOT EXISTS user_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL CHECK (BTRIM(title) <> ''),
    content TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_records_owner
    ON user_records (owner_id);
