#!/bin/sh
set -e
docker exec postgres15 bash -c "pg_dump -U postgres -d \"$2\" -f /usr/dumps/\"$1.bin\" -F c"
docker cp postgres15:/usr/dumps/"$1.bin" ./"$3"/
#docker exec ae bash -c "pg_dump -U postgres -d \"$2\" /var/lib/postgresql/data/pgdata/\"$1\" -f \"$3\" -F c"
#docker cp ae:/var/lib/postgresql/data/pgdata/dumps/"$1.bin" ./"$3"/
exit