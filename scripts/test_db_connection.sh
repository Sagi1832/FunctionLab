#!/bin/sh
# Script to test database connection from api container
# Usage: docker exec -it functionlab-api sh /path/to/test_db_connection.sh

set -e

DB_URL="${DATABASE_URL:-postgresql+asyncpg://functionlab:functionlab_pw@db:5432/functionlab}"

echo "Testing database connection..."
echo "Connection URL (masked): $(echo $DB_URL | sed 's/:\([^@]*\)@/:***@/')"

# Extract components from URL for psql if available
if command -v psql >/dev/null 2>&1; then
    echo "psql found, attempting direct connection..."
    # Parse URL components (simplified)
    # Format: postgresql+asyncpg://user:pass@host:port/db
    HOST=$(echo $DB_URL | sed -n 's|.*@\([^:]*\):.*|\1|p')
    PORT=$(echo $DB_URL | sed -n 's|.*:\([0-9]*\)/.*|\1|p')
    USER=$(echo $DB_URL | sed -n 's|.*://\([^:]*\):.*|\1|p')
    PASS=$(echo $DB_URL | sed -n 's|.*://[^:]*:\([^@]*\)@.*|\1|p')
    DB=$(echo $DB_URL | sed -n 's|.*/\([^?]*\).*|\1|p')
    
    PGPASSWORD=$PASS psql -h $HOST -p ${PORT:-5432} -U $USER -d $DB -c "SELECT 1 as test;" && {
        echo "✓ Direct psql connection successful"
    } || {
        echo "✗ Direct psql connection failed"
        exit 1
    }
else
    echo "psql not found in container. Install with: apt-get update && apt-get install -y postgresql-client"
    echo "Or test via Python:"
    python3 <<EOF
import asyncio
import asyncpg
import os

async def test():
    db_url = os.getenv("DATABASE_URL", "$DB_URL")
    # Convert postgresql+asyncpg:// to connection params
    if db_url.startswith("postgresql+asyncpg://"):
        db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
    
    # Parse for asyncpg
    import re
    m = re.match(r"postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)", db_url)
    if m:
        user, password, host, port, database = m.groups()
        try:
            conn = await asyncpg.connect(
                host=host,
                port=int(port),
                user=user,
                password=password,
                database=database
            )
            result = await conn.fetchval("SELECT 1")
            await conn.close()
            print(f"✓ Python asyncpg connection successful: {result}")
        except Exception as e:
            print(f"✗ Python asyncpg connection failed: {e}")
            exit(1)
    else:
        print("✗ Could not parse DATABASE_URL")
        exit(1)

asyncio.run(test())
EOF
fi


