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
    role_id SERIAL REFERENCES role (id) ON DELETE CASCADE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS subcategory (
    id SERIAL PRIMARY KEY,
    name varchar(32) UNIQUE NOT NULL,
    "order" integer NOT NULL
);

CREATE TABLE IF NOT EXISTS product (
    id SERIAL PRIMARY KEY,
    name varchar(32) UNIQUE NOT NULL,
    short_name varchar(20) UNIQUE NOT NULL,
    is_priority bool DEFAULT FALSE NOT NULL,
    price float NOT NULL,
    category categories NOT NULL,
    subcategory_id SERIAL REFERENCES subcategory (id) ON DELETE CASCADE NOT NULL
);

CREATE TABLE IF NOT EXISTS product_date (
    id SERIAL PRIMARY KEY,
    start_date TIMESTAMPTZ NOT NULL,
    end_date TIMESTAMPTZ NOT NULL,
    product_id SERIAL REFERENCES product (id) ON DELETE CASCADE NOT NULL
    CONSTRAINT valid_date_range CHECK (start_date < end_date)
);

CREATE TABLE IF NOT EXISTS product_ingredient (
    id SERIAL PRIMARY KEY,
    name varchar(32) NOT NULL,
    price float NOT NULL,
    product_id SERIAL REFERENCES product (id) ON DELETE CASCADE NOT NULL
);

CREATE TABLE IF NOT EXISTS product_role (
    id SERIAL PRIMARY KEY,
    role_id SERIAL REFERENCES role (id) ON DELETE CASCADE NOT NULL,
    product_id SERIAL REFERENCES product (id) ON DELETE CASCADE NOT NULL
);

CREATE TABLE IF NOT EXISTS product_variant (
    id SERIAL PRIMARY KEY,
    name varchar(32) NOT NULL,
    price float NOT NULL,
    product_id SERIAL REFERENCES product (id) ON DELETE CASCADE NOT NULL
);

CREATE UNIQUE INDEX idx_unique_product_date
ON product_date (product_id, start_date, end_date);

CREATE UNIQUE INDEX idx_unique_product_ingredient
ON product_ingredient (name, product_id);

CREATE UNIQUE INDEX idx_unique_product_role
ON product_role (role_id, product_id);

CREATE UNIQUE INDEX idx_unique_product_variant
ON product_variant (name, product_id);
