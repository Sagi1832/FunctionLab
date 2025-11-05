#!/bin/sh
# Script to reset postgres password from within the postgres container
# Usage: docker exec -it functionlab-postgres sh /path/to/reset_db_password.sh

set -e

NEW_PASSWORD="${POSTGRES_PASSWORD:-functionlab_pw}"
NEW_USER="${POSTGRES_USER:-functionlab}"
NEW_DB="${POSTGRES_DB:-functionlab}"

echo "Resetting password for user: $NEW_USER"
echo "Target database: $NEW_DB"

# Connect as postgres superuser and reset the password
psql -v ON_ERROR_STOP=1 <<EOF
-- Ensure user exists
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = '$NEW_USER') THEN
        CREATE USER $NEW_USER WITH PASSWORD '$NEW_PASSWORD';
        RAISE NOTICE 'User $NEW_USER created';
    ELSE
        RAISE NOTICE 'User $NEW_USER already exists';
    END IF;
END
\$\$;

-- Reset password
ALTER USER $NEW_USER WITH PASSWORD '$NEW_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE $NEW_DB TO $NEW_USER;

-- Grant schema privileges
\c $NEW_DB
GRANT ALL PRIVILEGES ON SCHEMA public TO $NEW_USER;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $NEW_USER;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $NEW_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $NEW_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $NEW_USER;

-- Verify
\du $NEW_USER
SELECT 'Password reset successful' AS status;
EOF

echo "Password reset complete. Testing connection..."
PGPASSWORD=$NEW_PASSWORD psql -h localhost -U $NEW_USER -d $NEW_DB -c "SELECT 1 as test;" || {
    echo "ERROR: Connection test failed!"
    exit 1
}

echo "Connection test successful!"


