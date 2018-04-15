drop table if exists users;
create table users (
  id integer primary key autoincrement,
  full_name text CHECK( LENGTH(full_name) <= 200 ) not null,
  small_name text CHECK( LENGTH(small_name) <= 100 ) not null unique,
  role text not null,
  access_level text not null,
  last_access_date date,
  last_access_hour time
);