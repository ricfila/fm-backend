CREATE TYPE paper_sizes AS ENUM ('A4', 'A5');
CREATE TYPE categories AS ENUM ('food', 'drink');

CREATE TABLE IF NOT EXISTS role (
    id SERIAL PRIMARY KEY,
    name varchar(32) UNIQUE NOT NULL,
    can_administer bool DEFAULT FALSE NOT NULL,
    can_order bool DEFAULT FALSE NOT NULL,
    can_statistics bool DEFAULT FALSE NOT NULL,
    can_priority_statistics bool DEFAULT FALSE NOT NULL,
    paper_size paper_sizes DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS "user" (
    id SERIAL PRIMARY KEY,
    username varchar(32) UNIQUE NOT NULL,
    password text NOT NULL,
    role_id SERIAL REFERENCES role (id) NOT NULL,
    created_at BIGINT DEFAULT extract(EPOCH FROM now())::int
);

CREATE TABLE IF NOT EXISTS subcategories (
    id SERIAL PRIMARY KEY,
    name varchar(32) UNIQUE NOT NULL,
    "order" integer UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS product (
    id SERIAL PRIMARY KEY,
    name varchar(32) UNIQUE NOT NULL,
    short_name varchar(20) UNIQUE NOT NULL,
    is_priority bool DEFAULT FALSE NOT NULL,
    price float NOT NULL,
    category categories NOT NULL,
    subcategory_id SERIAL REFERENCES subcategories (id) NOT NULL
);

CREATE TABLE IF NOT EXISTS product_ingredient (
    id SERIAL PRIMARY KEY,
    name varchar(32) UNIQUE NOT NULL,
    price float NOT NULL,
    product_id SERIAL REFERENCES product (id) NOT NULL
);

CREATE TABLE IF NOT EXISTS product_date (
    id SERIAL PRIMARY KEY,
    start_date BIGINT DEFAULT extract(EPOCH FROM now())::int,
    end_date BIGINT DEFAULT extract(EPOCH FROM now())::int,
    product_id SERIAL REFERENCES product (id) NOT NULL
);

CREATE TABLE IF NOT EXISTS product_variant (
    id SERIAL PRIMARY KEY,
    name varchar(32) UNIQUE NOT NULL,
    price float NOT NULL,
    product_id SERIAL REFERENCES product (id) NOT NULL
);

CREATE TABLE IF NOT EXISTS product_role (
    id SERIAL PRIMARY KEY,
    role_id SERIAL REFERENCES role (id) NOT NULL,
    product_id SERIAL REFERENCES product (id) NOT NULL
);
