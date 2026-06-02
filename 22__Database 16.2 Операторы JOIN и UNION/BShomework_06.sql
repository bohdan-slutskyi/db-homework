USE northwind;

/* 01 Выведите одним запросом с использованием UNION столбцы id, employee_id из таблицы orders
и соответствующие им столбцы из таблицы purchase_orders.
В таблице purchase_orders  created_by соответствует employee_id.*/

SELECT * FROM orders;
SELECT * FROM purchase_orders;
SELECT
    id,
    employee_id
FROM orders
UNION
SELECT
    id,
    created_by AS employee_id
FROM purchase_orders;

/* 02 Из предыдущего запроса удалите записи там где employee_id не имеет значения.
Добавьте дополнительный столбец со сведениями из какой таблицы была взята запись. */

SELECT * FROM orders;
SELECT * FROM purchase_orders;
SELECT
    id,
    employee_id,
    'orders' AS source_table
FROM orders
WHERE employee_id IS NOT NULL
UNION
SELECT
    id,
    created_by AS employee_id,
    'purchase_orders' AS source_table
FROM purchase_orders
WHERE created_by IS NOT NULL;


/* 03 Выведите все столбцы таблицы order_details,
 а также дополнительный столбец payment_method из таблицы purchase_orders.
 Оставьте только заказы для которых известен payment_method.

 (Таблицы order_details и purchase_orders связаны по purchase_order_id)
 */

SELECT * FROM order_details;
SELECT * FROM purchase_orders;
SELECT
    od.*,
    po.payment_method
FROM order_details AS od
INNER JOIN purchase_orders AS po
    ON od.purchase_order_id = po.id
WHERE po.payment_method IS NOT NULL;


-- 04 Выведите заказы orders и фамилии клиентов customers для тех заказов по которым были инвойсы таблица invoices.
SELECT * FROM orders;
SELECT * FROM customers;
SELECT * FROM invoices;
SELECT
    o.*,
    c.last_name
FROM orders AS o
INNER JOIN customers AS c
    ON o.customer_id = c.id
INNER JOIN invoices AS i
    ON o.id = i.order_id;


-- 05 Подсчитайте количество инвойсов для каждого клиента из предыдущего запроса.
SELECT
    c.id AS customer_id,
    c.first_name,
    c.last_name,
    COUNT(i.id) AS invoice_count
FROM orders AS o
INNER JOIN customers AS c
    ON o.customer_id = c.id
INNER JOIN invoices AS i
    ON o.id = i.order_id
GROUP BY
    c.id,
    c.last_name;
