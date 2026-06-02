USE northwind;
SELECT * FROM purchase_order_details;

-- 01 Для каждого заказа purchase_order_id выведите минимальный, максимальный и средний unit_cost.
SELECT purchase_order_id,
       MIN(unit_cost) OVER (PARTITION BY purchase_order_id) AS min_unit_cost,
       MAX(unit_cost) OVER (PARTITION BY purchase_order_id) AS max_unit_cost,
       AVG(unit_cost) OVER (PARTITION BY purchase_order_id) AS avg_unit_cost
FROM purchase_order_details;

-- 02 ставьте только уникальные строки из предыдущего запроса.
SELECT DISTINCT purchase_order_id,
       MIN(unit_cost) OVER (PARTITION BY purchase_order_id) AS min_unit_cost,
       MAX(unit_cost) OVER (PARTITION BY purchase_order_id) AS max_unit_cost,
       AVG(unit_cost) OVER (PARTITION BY purchase_order_id) AS avg_unit_cost
FROM purchase_order_details;

/* 03 Посчитайте стоимость продукта в заказе как quantity * unit_cost.
Выведите суммарную стоимость продуктов с помощью оконной функции
для каждого purchase_order_id.
Сделайте то же самое с помощью GROUP BY. */
-- OVER (с повторами номеров заказа)
SELECT purchase_order_id, 
       SUM(quantity * unit_cost) OVER (PARTITION BY purchase_order_id) AS total_cost
FROM purchase_order_details;
    
-- OVER (без повторов номеров заказа)
SELECT DISTINCT purchase_order_id, 
       SUM(quantity * unit_cost) OVER (PARTITION BY purchase_order_id) AS total_cost
FROM purchase_order_details;

-- GROUP BY
SELECT purchase_order_id, 
       SUM(quantity * unit_cost) AS total_cost
FROM purchase_order_details
GROUP BY purchase_order_id;

/* 04 Посчитайте количество заказов по дате получения и posted_to_inventory.
Если оно превышает 1 то выведите '>1' в противном случае '=1'.*/
SELECT date_received,
       posted_to_inventory,
       CASE
           WHEN COUNT(*) OVER (
               PARTITION BY date_received, posted_to_inventory
           ) > 1 THEN '>1'
           ELSE '=1'
       END AS order_count
FROM purchase_order_details;

-- 05 Выведите posted_to_inventory, date_received и вычисленный столбец.
SELECT DISTINCT posted_to_inventory,
       date_received,
       CASE
           WHEN COUNT(*) OVER (
               PARTITION BY posted_to_inventory, date_received
           ) > 1 THEN '>1'
           ELSE '=1'
       END AS order_count
FROM purchase_order_details;
