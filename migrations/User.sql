select 'create database "User"' where not exists (select from pg_database where datname = 'User')\gexec
\c User;
create table if not exists users_table
(
    user_id serial primary key,
    username text not null,
    password text not null,
    realname text not null,
    user_desc text not null default '',
    avatar text not null default '',
    roles json[],
    sex boolean
);
insert into users_table(username, password,realname, roles,sex)
    values (
        'admin',
        'password',
        'admin',
        array['{"value":"admin","role_name":"Super Admin"}','{"value":"customer", "role_name":"Customer"}']::json[],
        True
    );