DROP TABLE IF EXISTS post;

create table post (
  id integer primary key autoincrement,
  created timestamp not null default current_timestamp ,
  title text not null ,
  description text not null ,
  color text not null,
  likes int not null
);