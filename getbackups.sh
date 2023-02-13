#!/bin/sh
set -e
docker exec postgres15 bash -c "ls --sort=t /usr/backups/"
#docker exec ae bash -c "ls --sort=t /var/lib/postgresql/data/backups/"
exit