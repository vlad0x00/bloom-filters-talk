# SQLite Bloom filter demo

SQLite (3.38+) builds a Bloom filter automatically for some joins. This demo runs the same join with and without it.

Requires the `sqlite3` command-line shell, version 3.38 or newer. The benchmark also needs [hyperfine](https://github.com/sharkdp/hyperfine).

## Run

From this directory:

```sh
sqlite3 demo.db < 1_setup.sql          # once: creates demo.db (~240 MB, ~2 s)
sqlite3 demo.db < 2_with_bloom.sql     # join with the Bloom filter
sqlite3 demo.db < 3_without_bloom.sql  # same join, Bloom filter turned off
./4_benchmark.sh                       # 20 runs of each, with statistics
```

## What to look for

| Script | Plan contains | Time (example) |
|---|---|---|
| `2_with_bloom.sql` | `BLOOM FILTER ON customers (id=?)` | ~0.6 s |
| `3_without_bloom.sql` | no Bloom filter line | ~1.4 s |

Both return the same count (19800). Of the 20M orders, 99.9% have no matching customer. The Bloom filter rejects those with a few bit checks, instead of a lookup in `customers`.

`.timer on` prints one `Run Time` line per statement. The first is `explain query plan` (planning only, ~0 ms); the second is the query. `real` is wall-clock time; `user` and `sys` are CPU time in userspace and the kernel.

`explain query plan` prints how SQLite will run the query. It is the only place the Bloom filter is visible. `.testctrl optimizations 0x80000` disables SQLite's Bloom filter optimization for that session.

## Benchmark (example output)

```
with Bloom filter:     605.8 ms ±  38.7 ms   (range 562.6 ms … 698.3 ms, 20 runs)
without Bloom filter:  1.335 s  ±  0.052 s   (range 1.285 s  … 1.431 s,  20 runs)

with Bloom filter ran 2.20 ± 0.16 times faster
```

The ranges don't overlap: the slowest run with the filter is faster than the fastest run without it.
