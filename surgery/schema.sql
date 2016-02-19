drop table if exists queries;
create table queries (
  id integer primary key autoincrement,
  query text not null,
  depth int not null,
  minlength int not null,
  stopwords text not null,
  link text not null,
  timestr text not null
);
