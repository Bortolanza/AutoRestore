#!/bin/sh
set -e
docker exec postgres15 bash -c "df -h"
#docker exec ae bash -c "df -h"
exit