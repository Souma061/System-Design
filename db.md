-- SELECT VERSION();
-- CREATE TABLE  IF not EXISTS users (
--     user_id SERIAL PRIMARY KEY,
--     username VARCHAR(50) NOT null UNIQUE,
--     email VARCHAR(100) NOT null UNIQUE,
--     password_hash VARCHAR(255) NOT null,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );
-- SELECT * FROM users;
-- INSERT into users (username,email,password_hash) VALUES (
-- 'souma',
-- 'john.does@example.com', 'hashed_password_123'
-- );
-- SELECT *
-- FROM users;
-- INSERT into users (username, email, password_hash)
-- VALUES (
--         'Ritam Chakrabortys',
--         'ritam.chakrabortys@example.com',
--         'hashed_password_123'
--     );
-- SELECT *
-- -- FROM users;


-- UPDATE users
-- SET email = 'new.email@example.com'
-- WHERE username = 'souma';

-- SELECT *
-- FROM users;


-- INSERT INTO users (username, email, password_hash)
-- SELECT 'user_' || gs,
--     'user_' || gs || '@example.com',
--     'hashed_password_' || gs
-- FROM generate_series(10001,40000) AS gs;



SELECT * FROM users;

-- INSERT INTO users (username, email, password_hash)
-- VALUES (
--         'soumabrata_ghosh',
--         'soumabrata@example.com',
--         'hashed_password'
--     );


-- select * from users WHERE username = 'soumabrata_ghosh';

-- alter TABLE users ADD COLUMN city VARCHAR(100);

-- SELECT user_id,
--     username,
--     city
-- FROM users
-- LIMIT 5;


-- UPDATE users
-- SET city = CASE
--     WHEN user_id % 5 = 0 THEN 'New York'
--     WHEN user_id % 5 = 1 THEN 'Los Angeles'
--     WHEN user_id % 5 = 2 THEN 'Chicago'
--     WHEN user_id % 5 = 3 THEN 'Kolkata'
--     ELSE 'Phoenix'

--     END;


-- SELECT city,
--     COUNT(*)
-- FROM users
-- GROUP BY city;

-- EXPLAIN ANALYZE
-- SELECT *
-- FROM users
-- WHERE city = 'Kolkata';


-- CREATE INDEX idx_users_city ON users(city);

-- EXPLAIN ANALYZE
-- SELECT *
-- FROM users
-- WHERE city = 'Kolkata';


-- DROP INDEX idx_users_city;


-- EXPLAIN ANALYZE
-- SELECT *
-- FROM users
-- WHERE city = 'Kolkata';


-- CREATE INDEX idx_users_city ON users(city);
-- EXPLAIN ANALYZE
-- SELECT *
-- FROM users
-- WHERE city = 'Kolkata';


-- UPDATE users
-- SET city = 'Tokyo'
-- WHERE user_id = 1234;


-- EXPLAIN ANALYZE
-- SELECT *
-- FROM users
-- WHERE city = 'Tokyo';


-- SELECT * FROM users
-- WHERE city = 'Tokyo';


-- UPDATE users
-- SET city = 'Tokyo'
-- WHERE user_id % 5 = 4;


-- EXPLAIN ANALYZE
-- SELECT *
-- FROM users
-- WHERE city = 'Tokyo';

-- EXPLAIN ANALYZE
-- SELECT *
-- FROM users
-- WHERE city = 'Tokyo';



-- CREATE TABLE posts (
--     post_id serial PRIMARY KEY,
--     user_id INT REFERENCES users(user_id),
--     CONTENT TEXT,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );

-- INSERT INTO posts (user_id, content)
-- SELECT user_id,
--     'Post by ' || username
-- FROM users;


-- select * from posts;



-- inner join

-- CREATE INDEX idx_posts_user_id ON posts(user_id);

-- EXPLAIN ANALYZE
-- SELECT u.username,p.content
-- FROM users u
-- JOIN posts p on u.user_id = p.user_id
-- WHERE u.city = 'Kolkata';


-- Only one user's posts -- very selective
-- EXPLAIN ANALYZE
-- SELECT u.username,
--     p.content
-- FROM users u
--     JOIN posts p ON u.user_id = p.user_id
-- WHERE u.username = 'user_10001';
-- `



-- UPDATE users
-- SET city = 'Berlin'
-- WHERE city = 'Tokyo';


-- UPDATE users
-- SET city = 'Tokyo'
-- WHERE city = 'Berlin';


-- UPDATE users
-- SET city = 'Berlin'
-- WHERE city = 'Tokyo';


-- SELECT relname,
--     n_live_tup,
--     n_dead_tup
-- FROM pg_stat_user_tables
-- WHERE relname = 'users';


-- VACUUM users;

-- SELECT relname,
--     n_live_tup,
--     n_dead_tup
-- FROM pg_stat_user_tables
-- WHERE relname = 'users';


-- Generate dead tuples by updating same rows repeatedly
-- UPDATE users
-- SET city = 'Berlin'
-- WHERE city = 'Tokyo';
-- UPDATE users
-- SET city = 'Tokyo'
-- WHERE city = 'Berlin';
-- UPDATE users
-- SET city = 'Berlin'
-- WHERE city = 'Tokyo';
-- -- Check IMMEDIATELY before autovacuum kicks in
-- SELECT relname,
--     n_live_tup,
--     n_dead_tup
-- FROM pg_stat_user_tables
-- WHERE relname = 'users';



-- Select all

SET enable_nestloop = off;
-- Use EXPLAIN ANALYZE to diagnose query performance

EXPLAIN analyze
SELECT u.username,
    p.content FROM users u
    JOIN posts p on u.user_id = p.user_id
WHERE u.city = 'Kolkata';



