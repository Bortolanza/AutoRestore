#!/bin/sh
set -e
touch -m /app/bases/"$1"
#docker cp /app/bases/"$1" ae:/var/lib/postgresql/data/backups/
docker cp /app/bases/"$1" postgres15:/usr/backups/
exit
