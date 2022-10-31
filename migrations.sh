#!/bin/bash
set -e
psql -Upostgres -f /migrations/User.sql
