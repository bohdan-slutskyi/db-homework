-- ВНИМАНИЕ!!!
-- Все запросы пишем в интерфейсе DBeaver. На платформу загружаем скрины выполненных запросов!


USE northwind;

-- 1. Выберите только те строки из таблицы suppliers где company имеет значение Supplier A.
SELECT *
FROM suppliers
WHERE company = 'Supplier A';

-- 2. Вывести все строки из order_details там, где purchase_order_id не указано.
-- Дополнительно создать столбец total_price как quantity * unit_price.
SELECT *, quantity * unit_price AS total_price
FROM order_details
WHERE purchase_order_id IS NULL;

-- 3. Выведите какая дата будет через 51 день.
SELECT CURRENT_DATE + INTERVAL 51 DAY AS date_after_51_days;

-- 4. Посчитайте количество уникальных заказов purchase_order_id.
SELECT COUNT(DISTINCT purchase_order_id) AS unique_purchase_orders_count
FROM order_details;

-- 5. Выведите все столбцы order_details,
-- а также payment_method из purchase_orders.
-- Оставьте только заказы, для которых известен payment_method.
SELECT od.*, po.payment_method
FROM order_details AS od
JOIN purchase_orders AS po ON od.purchase_order_id = po.id
WHERE po.payment_method IS NOT NULL;