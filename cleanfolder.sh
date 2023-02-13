#!/bin/sh
set -e
#docker exec ae bash -c "rm /var/lib/postgresql/data/backups/\"$1\""
docker exec postgres15 bash -c "rm /usr/backups/\"$1\""
exit