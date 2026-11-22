-- Join with SQLite's Bloom filter (the default).

.timer on

explain query plan
  select count(*) from orders join customers on orders.customer_id = customers.id;

select count(*) from orders join customers on orders.customer_id = customers.id;
