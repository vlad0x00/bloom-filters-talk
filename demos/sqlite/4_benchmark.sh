#!/usr/bin/env bash
# Runs the join many times with and without the Bloom filter, using hyperfine.
# Requires: hyperfine, and demo.db created by 1_setup.sql.
set -euo pipefail
cd "$(dirname "$0")"

QUERY="select count(*) from orders join customers on orders.customer_id = customers.id;"

hyperfine --shell=none --warmup 3 --runs 10 \
  --command-name "with Bloom filter" \
  "sqlite3 demo.db '$QUERY'" \
  --command-name "without Bloom filter" \
  "sqlite3 -cmd '.testctrl optimizations 0x80000' demo.db '$QUERY'"
