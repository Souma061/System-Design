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

-- select user_id,title,created_at,row_number()  over (PARTITION BY user_id ORDER BY created_at) as post_number from posts;


-- we can use window function in many real world scenarios, for example, we can use window function to get the top 3 posts for each user based on the created_at column.Leaderboard or ranking systems often use window functions to rank users based on their scores or achievements. In analytics, window functions can be used to calculate moving averages, cumulative sums, or running totals over a specified range of data. They are also useful in financial applications for calculating metrics like rolling returns or volatility over time. Additionally, window functions can help in identifying trends and patterns in time-series data, making them valuable for forecasting and predictive modeling.


-- alter table posts add COLUMN parent_id int references posts(id);

-- select column_name,data_type from information_schema.columns where table_name='posts';


-- creating a comment thread

-- insert into posts (id, user_id, title, content, created_at, parent_id) values (4001, 1, 'Comment on Post 1', 'This is a comment on post 1.', NOW(), 1);


-- SELECT MAX(id)
-- FROM posts;

-- WITH root AS (
--     INSERT INTO posts (id, user_id, title, content, parent_id)
--     VALUES (
--             8001,
--             1,
--             'Root Post',
--             'What is the best way to learn SQL?',
--             NULL
--         )
--     RETURNING id
-- ),
-- comments AS (
--     INSERT INTO posts (id, user_id, title, content, parent_id)
--     VALUES (
--             8002,
--             2,
--             'Comment A',
--             'Start with SELECT basics',
--             8001
--         ),
--         (
--             8003,
--             3,
--             'Comment B',
--             'Practice with real datasets',
--             8001
--         )
--     RETURNING id
-- ),
-- replies AS (
--     INSERT INTO posts (id, user_id, title, content, parent_id)
--     VALUES (
--             8004,
--             4,
--             'Reply to A-1',
--             'Agreed, then move to joins',
--             8002
--         ),
--         (
--             8005,
--             5,
--             'Reply to A-2',
--             'I would add window functions early',
--             8002
--         )
--     RETURNING id
-- )
-- INSERT INTO posts (id, user_id, title, content, parent_id)
-- VALUES (
--         8006,
--         6,
--         'Reply to A-1-1',
--         'Joins confused me at first too',
--         8004
--     );


-- select id,title,parent_id from posts where id >= 8001 ORDER BY id;


-- with RECURSIVE comment_tree as (
--     --1 base case: select the root post
--     select id,user_id,title,content,parent_id,0 as depth from posts WHERE id = 8001

--     UNION ALL


--     --2 find child comments for each post in the previous level

--     select p.id,p.user_id,p.title,p.content,p.parent_id,ct.depth + 1 as depth from posts p
--     inner join comment_tree ct on p.parent_id = ct.id

-- )
-- SELECT * FROM comment_tree ORDER BY depth,id;


-- Base case
--     runs once: it grabs just the root post (id = 8001),
--     and starts a depth counter at 0.Recursive case
--         then runs repeatedly: it joins posts back to comment_tree — but comment_tree at this point only has the row(s) added by the previous iteration.So on the first recursive pass,
--         it finds all posts whose parent_id matches the root (8002, 8003),
--         and stamps them depth = 1.On the next pass,
--         it looks for posts whose parent_id matches those newly - found rows (8002, 8003),
--         giving 8004,
--         8005 at depth = 2.It keeps going — next pass finds 8006 (parent is 8004) at depth = 3.It stops automatically once a pass finds zero new rows (
--             no post has any of the current row 's id as its parent_id).



-- breaking


select root.id as root_id, root.title as root_title,c1.id as level1_id, c1.title as level1_title,c2.id as level2_id, c2.title as level2_title, c3.id as level3_id, c3.title as level3_title from posts root left JOIN posts
    c1 on c1.parent_id = root.id
left JOIN posts c2 on c2.parent_id = c1.id
left JOIN posts c3 on c3.parent_id = c2.id
where root.id = 8001


-- here's what happens in the query above: The root post (id = 8001) is selected first. Then, a LEFT JOIN is performed to find all level 1 comments (c1) that have the root post as their parent. Next, another LEFT JOIN is done to find level 2 comments (c2) that have level 1 comments as their parent. Finally, a third LEFT JOIN is performed to find level 3 comments (c3) that have level 2 comments as their parent. The WHERE clause filters the results to only include the root post with id = 8001. This structure allows us to retrieve the entire comment thread in a single query, with each level of comments represented in separate columns.
