#!/bin/sh
set -e
docker exec postgres15 bash -c "pg_restore -O -x -j 2 -U postgres -d \"$2\" /usr/backups/\"$1\""
#docker exec 921 bash -c "psql -U postgres -c \"ALTER DATABASE \\\"$2\\\" OWNER TO \\\"$3\\\"\""
#docker exec ae bash -c "/bin-psql-12.10/pg_restore -O -x -j 2 -U postgres -d \"$2\" /var/lib/postgresql/data/backups/\"$1\""
exit