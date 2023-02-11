#!/bin/sh
set -e
docker exec postgres15 bash -c "psql -U postgres -c \"SELECT pg_terminate_backend(pid) FROM pg_catalog.pg_stat_activity WHERE datname = '$1'\""
docker exec postgres15 bash -c "psql -U postgres -c \"DROP DATABASE IF EXISTS \\\"$1\\\"\""
#docker exec ae bash -c "psql -U postgres -c \"SELECT pg_terminate_backend(pid) FROM pg_catalog.pg_stat_activity WHERE datname = '$1'\""
#docker exec ae bash -c "psql -U postgres -c \"DROP DATABASE IF EXISTS \\\"$1\\\"\""
exit