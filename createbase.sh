#!/bin/sh
set -e
#docker exec ae bash -c "psql -U postgres -c \"CREATE DATABASE \\\"$1\\\"\"" OWNER \\\"$2\\\"
docker exec postgres15 bash -c "psql -U postgres -c \"CREATE DATABASE \\\"$1\\\"\""
exit