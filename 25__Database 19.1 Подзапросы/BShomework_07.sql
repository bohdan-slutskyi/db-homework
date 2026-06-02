USE northwind;

SELECT * FROM products;
SELECT * FROM order_details;
SELECT * FROM orders;
SELECT * FROM customers;

/* 01 Вывести названия продуктов (таблица products),
включая количество заказанных единиц quantity для каждого продукта таблица order_details.
Решить задачу с помощью CTE и подзапроса. */

-- 1) CTE
WITH product_quantity AS (
    SELECT
        product_id,
        SUM(quantity) AS total_quantity
    FROM order_details
    GROUP BY product_id
)
SELECT
    p.product_name,
    pq.total_quantity
FROM products AS p
JOIN product_quantity AS pq
    ON p.id = pq.product_id;


-- 2) Подзапрос

SELECT
    p.product_name,
    pq.total_quantity
FROM products AS p
JOIN (
    SELECT
        product_id,
        SUM(quantity) AS total_quantity
    FROM order_details
    GROUP BY product_id
) AS pq
    ON p.id = pq.product_id;

/* 02 Найти все заказы таблица orders,
сделанные после даты самого первого заказа клиента Lee таблица customers. */

SELECT
    o.*
FROM orders AS o
WHERE o.order_date > (
    SELECT
        MIN(o2.order_date)
    FROM orders AS o2
    JOIN customers AS c
        ON o2.customer_id = c.id
    WHERE c.last_name = 'Lee'
);

-- 03 Найти все продукты таблицы products c максимальным target_level.

SELECT
    p.*
FROM products AS p
WHERE p.target_level = (
    SELECT
        MAX(target_level)
    FROM products
);
