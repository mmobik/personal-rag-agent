-- migrate.sql
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='users' AND column_name='user_type') THEN
        ALTER TABLE users ADD COLUMN user_type VARCHAR(50);
    END IF;
END $$;

UPDATE users SET user_type = 'telegram' WHERE telegram_id IS NOT NULL AND user_type IS NULL;
UPDATE users SET user_type = 'ui_admin' WHERE email IS NOT NULL AND user_type IS NULL;

CREATE TABLE IF NOT EXISTS telegram_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    telegram_id VARCHAR UNIQUE NOT NULL,
    username VARCHAR,
    first_name VARCHAR,
    last_name VARCHAR,
    chat_id VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

INSERT INTO telegram_profiles (user_id, telegram_id, username, first_name, last_name)
SELECT id, telegram_id, username, first_name, last_name
FROM users
WHERE telegram_id IS NOT NULL
ON CONFLICT (user_id) DO NOTHING;

CREATE TABLE IF NOT EXISTS ui_admin_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    full_name VARCHAR NOT NULL,
    role VARCHAR DEFAULT 'admin',
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

INSERT INTO ui_admin_profiles (user_id, full_name, role)
SELECT id, COALESCE(username, email), 'admin'
FROM users
WHERE user_type = 'ui_admin' 
  AND NOT EXISTS (SELECT 1 FROM ui_admin_profiles WHERE user_id = users.id);

ALTER TABLE users ALTER COLUMN user_type SET NOT NULL;

CREATE INDEX IF NOT EXISTS idx_telegram_profiles_telegram_id ON telegram_profiles(telegram_id);
CREATE INDEX IF NOT EXISTS idx_ui_admin_profiles_user_id ON ui_admin_profiles(user_id);

SELECT '✅ Migration completed!' as status;
SELECT user_type, COUNT(*) as count FROM users GROUP BY user_type;