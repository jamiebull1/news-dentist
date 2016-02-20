drop table if exists queries;
create table queries (
  id integer primary key autoincrement,
  username text not null,
  query text not null,
  depth int not null,
  minlength int not null,
  stopwords text not null,
  link text not null,
  timestr text not null
);
drop table if exists users;
create table users (
  id integer primary key autoincrement,
  username text not null unique,
  email text not null unique,
  hashpass text not null
);
