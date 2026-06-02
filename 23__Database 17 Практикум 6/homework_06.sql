USE northwind;

/* 01 Выведите одним запросом с использованием UNION столбцы id, employee_id из таблицы orders
и соответствующие им столбцы из таблицы purchase_orders.
В таблице purchase_orders  created_by соответствует employee_id.*/

SELECT * FROM orders;
SELECT * FROM purchase_orders;


/* 02 Из предыдущего запроса удалите записи там где employee_id не имеет значения.
Добавьте дополнительный столбец со сведениями из какой таблицы была взята запись. */

SELECT * FROM orders;
SELECT * FROM purchase_orders;



/* 03 Выведите все столбцы таблицы order_details,
 а также дополнительный столбец payment_method из таблицы purchase_orders.
 Оставьте только заказы для которых известен payment_method.

 (Таблицы order_details и purchase_orders связаны по purchase_order_id)
 */

SELECT * FROM order_details;
SELECT * FROM purchase_orders;



-- 04 Выведите заказы orders и фамилии клиентов customers для тех заказов по которым были инвойсы таблица invoices.
SELECT * FROM orders;
SELECT * FROM customers;
SELECT * FROM invoices;



-- 05 Подсчитайте количество инвойсов для каждого клиента из предыдущего запроса.

