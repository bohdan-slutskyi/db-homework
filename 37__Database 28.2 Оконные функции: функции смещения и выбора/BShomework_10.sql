USE northwind;
SELECT * FROM order_details;

-- 01. Для каждого product_id выведите inventory_id а также предыдущий и последующей inventory_id по убыванию quantity.

SELECT
    product_id,
    inventory_id,
    LAG(inventory_id) OVER (
        PARTITION BY product_id
        ORDER BY quantity DESC
    ) AS previous_inventory_id,
    LEAD(inventory_id) OVER (
        PARTITION BY product_id
        ORDER BY quantity DESC
    ) AS next_inventory_id
FROM order_details;

/* 02. Выведите максимальный и минимальный unit_price для каждого order_id с помощью функции FIRST_VALUE().
	   Выведите order_id и полученные значения. */

SELECT DISTINCT
    order_id,
    FIRST_VALUE(unit_price) OVER (
        PARTITION BY order_id
        ORDER BY unit_price DESC
    ) AS max_unit_price,
    FIRST_VALUE(unit_price) OVER (
        PARTITION BY order_id
        ORDER BY unit_price
    ) AS min_unit_price
FROM order_details;

/* 03. Выведите order_id и столбец с разницей между unit_price для каждого заказа и минимальным unit_price в рамках одного заказа.
! Задачу решить двумя способами - с помощью FIRST_VALUE() и MIN().*/

-- FIRST_VALUE

SELECT
    order_id,
    unit_price,
    unit_price - FIRST_VALUE(unit_price) OVER (
        PARTITION BY order_id
        ORDER BY unit_price
    ) AS diff_from_min_unit_price
FROM order_details
ORDER BY -- для удобства сравнения результатов
    order_id,
    unit_price;

-- MIN

SELECT
    order_id,
    unit_price,
    unit_price - MIN(unit_price) OVER (
        PARTITION BY order_id
    ) AS diff_from_min_unit_price
FROM order_details
ORDER BY -- для удобства сравнения результатов
    order_id,
    unit_price;

-- 04. Присвойте ранг каждой строке, используя RANK() по убыванию quantity.

SELECT
    order_id,
    product_id,
    inventory_id,
    quantity,
    RANK() OVER (
        ORDER BY quantity DESC
    ) AS quantity_rank
FROM order_details;

-- 05. Из предыдущего запроса выберите только строки с рангом до 10 включительно.

WITH ranked_order_details AS (
    SELECT
        order_id,
        product_id,
        inventory_id,
        quantity,
        RANK() OVER (
            ORDER BY quantity DESC
        ) AS quantity_rank
    FROM order_details
)
SELECT
    order_id,
    product_id,
    inventory_id,
    quantity,
    quantity_rank
FROM ranked_order_details
WHERE quantity_rank <= 10
ORDER BY quantity_rank;
