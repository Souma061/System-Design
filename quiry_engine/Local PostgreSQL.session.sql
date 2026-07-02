-- create DATABASE my_database;

-- use my_database;


-- Create a new table 'users' with a primary key and columns


-- CREATE TABLE users (
--     id SERIAL PRIMARY KEY,
--     username VARCHAR(50) NOT NULL UNIQUE,
--     email VARCHAR(100) NOT NULL UNIQUE,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );


-- create table posts (
--     id serial PRIMARY key,
--     user_id int references users(id),
--     title varchar(100) not NULL,
--     content text not NULL,
--     created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- )


-- SELECT * FROM users;

-- select * from posts;


-- INSERT INTO users (username, email) VALUES ('john_doe', 'john@example.com');

-- insert into posts (user_id, title, content) values (1, 'My First Post', 'This is the content of my first post.');



