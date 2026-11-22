# SQLite Bloom filter demo

SQLite (3.38+) builds a Bloom filter automatically for some joins. This demo runs the same join with and without it.

Requires the `sqlite3` command-line shell, version 3.38 or newer.

## Run

From this directory:

```sh
sqlite3 demo.db < 1_setup.sql          # once: creates demo.db (~25 MB)
sqlite3 demo.db < 2_with_bloom.sql
sqlite3 demo.db < 3_without_bloom.sql
```

## What to look for

| Script | Plan contains | Time (example) |
|---|---|---|
| `2_with_bloom.sql` | `BLOOM FILTER ON customers (id=?)` | ~60 ms |
| `3_without_bloom.sql` | no Bloom filter line | ~130 ms |

Both return the same count (1980). Of the 2M orders, 99.9% have no matching customer. The Bloom filter rejects those with a few bit checks, instead of a lookup in `customers`.

`explain query plan` prints how SQLite will run the query. It is the only place the Bloom filter is visible. `.testctrl optimizations 0x80000` disables SQLite's Bloom filter optimization for that session.
