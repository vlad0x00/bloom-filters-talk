-- Creates two tables in demo.db.
--   orders:    2,000,000 rows, each pointing to a customer_id from 0 to 99,999
--   customers: 100 rows (IDs 1000, 2000, ..., 100000)
-- Only ~0.1% of orders have a matching customer.

drop table if exists orders;
drop table if exists customers;

create table orders(id integer primary key, customer_id int);
create table customers(id int, name text);

insert into orders(customer_id)
  select value % 100000 from generate_series(1, 2000000);

insert into customers
  select value * 1000, 'customer ' || value from generate_series(1, 100);

analyze;
