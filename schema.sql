drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  description text not null,
  author text not null,
  price int not null,
  paid bool not null
);
