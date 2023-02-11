#!/bin/sh
set -e
#docker exec ae bash -c "ls -X /var/lib/postgresql/data/backups/"
docker exec postgres15 bash -c "ls -X /usr/backups/"
exit

