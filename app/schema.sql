-- create order_status types
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'available_order_status') THEN
        CREATE TYPE available_order_status AS ENUM
        (
            '0',
            '1',
            '2',
            '3'
        );
    END IF;
END$$;

-- create item_status types
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'available_item_status') THEN
        CREATE TYPE available_item_status AS ENUM
        (
            '0',
            '1',
            '2'
        );
    END IF;
END$$;

-- create item parking status
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'available_item_parking_status') THEN
        CREATE TYPE available_item_parking_status AS ENUM
        (
            '0',
            '1'
        );
    END IF;
END$$;

-- create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    points FLOAT,
    name VARCHAR(100),
    phone_number VARCHAR(50)
);

-- create orders table
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    order_mode VARCHAR,
    order_creation_date TIMESTAMP,
    order_finish_date TIMESTAMP,
    order_table INTEGER,
    order_status available_order_status,
    time_spent INTEGER,
    user_point FLOAT,
    buttons TEXT[],
    buttons_category TEXT[],

    CONSTRAINT fk_user
        FOREIGN KEY (user_id)
            REFERENCES users(id)
);

-- create orders_items table
CREATE TABLE IF NOT EXISTS orders_items (
    order_id INTEGER,
    item_id SERIAL PRIMARY KEY,
    item_name VARCHAR,
    item_quantity INTEGER,
    item_price FLOAT,
    item_status available_item_status,
    
    CONSTRAINT fk_order
        FOREIGN KEY (order_id) 
            REFERENCES orders(id)
);

-- create parking_items table
CREATE TABLE IF NOT EXISTS parking_items (
    item_id SERIAL PRIMARY KEY,
    user_id INTEGER,
    item_name VARCHAR,
    item_quantity INTEGER,
    item_parking_date TIMESTAMP,
    item_status available_item_parking_status,

    CONSTRAINT fk_user
        FOREIGN KEY (user_id)
            REFERENCES users(id)
);
