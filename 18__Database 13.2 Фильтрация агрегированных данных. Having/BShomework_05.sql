SELECT * FROM northwind.purchase_order_details;

-- 01 Подсчитайте основные статистики - среднее, сумму, минимум, максимум столбца unit_cost.

SELECT
    AVG(unit_cost) AS avg_unit_cost,
    SUM(unit_cost) AS total_unit_cost,
    MIN(unit_cost) AS min_unit_cost,
    MAX(unit_cost) AS max_unit_cost
FROM northwind.purchase_order_details;

-- 02 Подсчитайте количество уникальных заказов purchase_order_id.

SELECT COUNT(DISTINCT purchase_order_id) AS unique_purchase_orders
FROM northwind.purchase_order_details;

/* 03 Подсчитайте количество продуктов product_id в каждом заказе purchase_order_id.
   Отсортируйте полученные данные по убыванию количества. */

SELECT
    purchase_order_id,
    COUNT(product_id) AS product_count
FROM northwind.purchase_order_details
GROUP BY purchase_order_id
ORDER BY product_count DESC;

/* 04 Подсчитайте заказы по дате доставки date_received.
   Считаем только те продукты, количество quantity которых больше 30. */

SELECT
    date_received,
    COUNT(*) AS orders_count
FROM northwind.purchase_order_details
WHERE quantity > 30
GROUP BY date_received;

/* 05 Подсчитайте суммарную стоимость заказов в каждую из дат.
   Стоимость заказа - произведение quantity на unit_cost. */

SELECT
    date_received,
    SUM(quantity * unit_cost) AS total_orders_cost
FROM northwind.purchase_order_details
GROUP BY date_received;

/* 06 Сгруппируйте товары по unit_cost и вычислите среднее и максимальное
   значение quantity только для товаров, где purchase_order_id не больше 100. */

SELECT
    unit_cost,
    AVG(quantity) AS avg_quantity,
    MAX(quantity) AS max_quantity
FROM northwind.purchase_order_details
WHERE purchase_order_id <= 100
GROUP BY unit_cost;

/* 07 Выберите только строки, где есть значения в столбце inventory_id.
Создайте столбец category
   - если unit_cost > 20 то 'Expensive'
   - в остальных случаях  - 'others'.
Посчитайте количество продуктов в каждой категории. */

SELECT
    CASE
        WHEN unit_cost > 20 THEN 'Expensive'
        ELSE 'others'
    END AS category,
    COUNT(*) AS product_count
FROM northwind.purchase_order_details
WHERE inventory_id IS NOT NULL
GROUP BY category;
