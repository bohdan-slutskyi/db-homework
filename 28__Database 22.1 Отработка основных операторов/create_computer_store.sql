DROP DATABASE IF EXISTS computer_store;
CREATE DATABASE computer_store;
USE computer_store;
CREATE TABLE product (
    maker VARCHAR(10),
    model VARCHAR(50),
    type VARCHAR(50)
);
SELECT * -- посмотрим, что в таблице
FROM product;
INSERT INTO product
VALUES
    ('A', '1001', 'PC'),
    ('A', '1002', 'Laptop'),
    ('A', '1003', 'Printer'),

    ('B', '2001', 'PC'),
    ('B', '2002', 'Laptop'),
    ('B', '2003', 'Printer'),

    ('C', '3001', 'PC'),
    ('C', '3002', 'Laptop'),
    ('C', '3003', 'Printer'),

    ('D', '4001', 'PC'),
    ('D', '4002', 'Laptop'),
    ('D', '4003', 'Printer'),

    ('E', '5001', 'PC'),
    ('E', '5002', 'Laptop'),

    ('F', '6001', 'Printer'),
    ('F', '6002', 'Printer');

SELECT * -- посмотрим, что в таблице
FROM product;
CREATE TABLE pc (
    code INT PRIMARY KEY,
    model VARCHAR(50),
    speed SMALLINT,
    ram SMALLINT,
    hd REAL,
    cd VARCHAR(10),
    price DECIMAL(10, 2)
);
SELECT * -- посмотрим, что в таблице
FROM pc;
INSERT INTO pc
VALUES
    (1, '1001', 500, 64, 5, '12x', 450.00),
    (2, '2001', 750, 128, 10, '24x', 600.00),
    (3, '3001', 800, 128, 20, '24x', 850.00),
    (4, '4001', 600, 64, 10, '12x', 400.00),
    (5, '5001', 1000, 256, 40, '48x', 1200.00);
SELECT * -- посмотрим, что в таблице
FROM pc;

CREATE TABLE laptop (
    code INT PRIMARY KEY,
    model VARCHAR(50),
    speed SMALLINT,
    ram SMALLINT,
    hd REAL,
    price DECIMAL(10, 2),
    screen TINYINT
);

SELECT * -- посмотрим, что в таблице
FROM laptop;

INSERT INTO laptop
VALUES
    (1, '1002', 450, 64, 10, 1200.00, 12),
    (2, '2002', 600, 128, 20, 1500.00, 14),
    (3, '3002', 750, 256, 40, 1800.00, 15),
    (4, '4002', 500, 64, 8, 900.00, 13),
    (5, '5002', 700, 128, 12, 1100.00, 14);

SELECT * -- посмотрим, что в таблице
FROM laptop;

CREATE TABLE printer (
    code INT PRIMARY KEY,
    model VARCHAR(50),
    color CHAR(1),
    type VARCHAR(100),
    price DECIMAL(10, 2)
);

SELECT * -- посмотрим, что в таблице
FROM printer;

INSERT INTO printer
VALUES
    (1, '1003', 'y', 'Jet', 300.00),
    (2, '2003', 'n', 'Laser', 400.00),
    (3, '3003', 'y', 'Laser', 350.00),
    (4, '4003', 'n', 'Matrix', 200.00),
    (5, '6001', 'y', 'Jet', 250.00),
    (6, '6002', 'y', 'Laser', 250.00);

SELECT * -- посмотрим, что в таблице
FROM printer;