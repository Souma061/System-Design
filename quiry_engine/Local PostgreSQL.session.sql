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



-- update posts set title = 'updated title' where id = 1;


-- CREATE OR REPLACE FUNCTION seed_users(num_users INT DEFAULT 4000) RETURNS void AS $$ BEGIN
-- INSERT INTO users (username, email, created_at)
-- SELECT 'user_' || i AS username,
--     'user_' || i || '@example.com' AS email,
--     NOW() - (random() * INTERVAL '365 days') AS created_at
-- FROM generate_series(1, num_users) AS i;
-- END;
-- $$ LANGUAGE plpgsql;


-- SELECT seed_users(4000);
-- SELECT COUNT(*)
-- FROM users;
-- TRUNCATE posts RESTART IDENTITY CASCADE;
-- SELECT seed_users(4000);
-- SELECT COUNT(*)
-- FROM posts;


-- CREATE OR REPLACE FUNCTION seed_posts(num_posts INT DEFAULT 4000) RETURNS void AS $$ BEGIN
-- INSERT INTO posts (user_id, title, content, created_at)
-- SELECT
--     (random() * 4000 + 1)::int AS user_id,
--     'Post_' || i AS title,
--     'Content for post ' || i AS content,
--     NOW() - (random() * INTERVAL '365 days') AS created_at
-- FROM generate_series(1, num_posts) AS i;
-- END;
-- $$ LANGUAGE plpgsql;



-- select seed_posts(4000);


-- window functions

select user_id,title,created_at,row_number()  over (PARTITION BY user_id ORDER BY created_at) as post_number from posts;
