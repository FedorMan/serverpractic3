CREATE TABLE score(
  id serial primary key,
  file varchar(256),
  human_string varchar(64),
  expert_answer varchar(64),
  score double precision
);