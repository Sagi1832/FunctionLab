#!/bin/sh
# Comprehensive script to fix database authentication issues
# This script should be run from the host machine

set -e

echo "=== FunctionLab DB Auth Fix Script ==="
echo ""

# Step 1: Check if containers are running
echo "Step 1: Checking container status..."
if ! docker ps | grep -q functionlab-postgres; then
    echo "ERROR: functionlab-postgres container is not running"
    echo "Please start containers with: docker compose up -d"
    exit 1
fi

if ! docker ps | grep -q functionlab-api; then
    echo "WARNING: functionlab-api container is not running"
    echo "It will start after we fix the DB"
fi

echo "✓ Containers found"
echo ""

# Step 2: Verify postgres environment variables
echo "Step 2: Checking Postgres environment variables..."
POSTGRES_USER=$(docker exec functionlab-postgres printenv POSTGRES_USER || echo "functionlab")
POSTGRES_PASSWORD=$(docker exec functionlab-postgres printenv POSTGRES_PASSWORD || echo "functionlab_pw")
POSTGRES_DB=$(docker exec functionlab-postgres printenv POSTGRES_DB || echo "functionlab")

echo "  POSTGRES_USER: $POSTGRES_USER"
echo "  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:0:4}***"
echo "  POSTGRES_DB: $POSTGRES_DB"
echo ""

# Step 3: Reset the password in Postgres
echo "Step 3: Resetting Postgres user password..."
docker exec -e POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
           -e POSTGRES_USER="$POSTGRES_USER" \
           -e POSTGRES_DB="$POSTGRES_DB" \
           functionlab-postgres psql -U postgres <<EOF
-- Ensure user exists and has correct password
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = '$POSTGRES_USER') THEN
        CREATE USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD';
        RAISE NOTICE 'User $POSTGRES_USER created';
    ELSE
        ALTER USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD';
        RAISE NOTICE 'Password reset for user $POSTGRES_USER';
    END IF;
END
\$\$;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO $POSTGRES_USER;
\c $POSTGRES_DB
GRANT ALL PRIVILEGES ON SCHEMA public TO $POSTGRES_USER;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $POSTGRES_USER;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $POSTGRES_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $POSTGRES_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $POSTGRES_USER;
EOF

echo "✓ Password reset complete"
echo ""

# Step 4: Test connection from Postgres container
echo "Step 4: Testing connection from Postgres container..."
docker exec -e PGPASSWORD="$POSTGRES_PASSWORD" \
           functionlab-postgres \
           psql -h 127.0.0.1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT 1 as test;" && {
    echo "✓ Connection test successful from Postgres container"
} || {
    echo "✗ Connection test failed from Postgres container"
    exit 1
}
echo ""

# Step 5: Check API container DATABASE_URL
echo "Step 5: Checking API container DATABASE_URL..."
if docker ps | grep -q functionlab-api; then
    API_DB_URL=$(docker exec functionlab-api printenv DATABASE_URL || echo "NOT SET")
    if [ "$API_DB_URL" != "NOT SET" ]; then
        MASKED=$(echo "$API_DB_URL" | sed 's/:\([^@]*\)@/:***@/')
        echo "  DATABASE_URL (masked): $MASKED"
        
        # Verify it matches expected format
        if echo "$API_DB_URL" | grep -q "functionlab:functionlab_pw@db:5432/functionlab"; then
            echo "✓ DATABASE_URL matches expected configuration"
        else
            echo "⚠ WARNING: DATABASE_URL does not match expected configuration"
            echo "  Expected: postgresql+asyncpg://functionlab:functionlab_pw@db:5432/functionlab"
        fi
    else
        echo "⚠ WARNING: DATABASE_URL not set in API container"
    fi
else
    echo "  API container not running yet (this is OK)"
fi
echo ""

# Step 6: Final recommendations
echo "=== Next Steps ==="
echo "1. Restart the API container:"
echo "   docker compose restart api"
echo ""
echo "2. Check API logs for connection info:"
echo "   docker compose logs api | grep -i database"
echo ""
echo "3. Test the /health/db endpoint:"
echo "   curl http://localhost:8000/health/db"
echo ""
echo "4. If connection still fails, check:"
echo "   - Docker network connectivity: docker network inspect functionlab_default"
echo "   - Postgres logs: docker compose logs db"
echo "   - API logs: docker compose logs api"
echo ""
echo "=== Script Complete ==="


