#!/bin/sh
set -e

# Dynamically construct DATABASE_URL
export DATABASE_URL="postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@validator-db:5432/${POSTGRES_DB}?sslmode=disable"

echo "Running migrations with DATABASE_URL=${DATABASE_URL}"
dbmate -d "./migrations" --no-dump-schema migrate
