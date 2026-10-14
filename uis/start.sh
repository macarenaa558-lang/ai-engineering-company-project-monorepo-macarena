#!/bin/sh
set -e

(cd /app/website && npm run dev -- --host 0.0.0.0 --port 3000) &
(cd /app/backoffice && npm run dev -- --host 0.0.0.0 --port 3001) &

wait