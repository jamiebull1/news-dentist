drop table if exists queries;
create table queries (
  id integer primary key autoincrement,
  query text not null,
  depth int not null,
  link text not null
);
