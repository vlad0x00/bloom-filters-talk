-- The same join with the Bloom filter optimization turned off.

.testctrl optimizations 0x80000
.timer on

explain query plan
  select count(*) from orders join customers on orders.customer_id = customers.id;

select count(*) from orders join customers on orders.customer_id = customers.id;
