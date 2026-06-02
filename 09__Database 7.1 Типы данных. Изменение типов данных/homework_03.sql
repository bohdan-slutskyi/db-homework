-- 01 Выведите Ваш возраст на текущий день в секундах
-- Variant 1
SELECT TIMESTAMPDIFF(SECOND, '1977-01-02', NOW()) AS age_in_seconds;
-- Variant 2
SELECT TIMESTAMPDIFF(SECOND, '1977-01-02', CURRENT_TIMESTAMP) AS age_in_seconds;

-- 02 Выведите какая дата будет через 51 день
-- Variant 1 
SELECT DATE_ADD(NOW(), INTERVAL 51 DAY) AS future_date;

-- Variant 2 
SELECT NOW() + INTERVAL 51 DAY AS future_date;

-- Variant 3 
SELECT DATE_ADD(CURDATE(), INTERVAL 51 DAY) AS future_date;

-- Variant 4 
SELECT CURRENT_DATE + INTERVAL 51 DAY AS future_date;

-- Variant 5 
SELECT DATE_SUB(NOW(), INTERVAL -51 DAY) AS future_date;


/* 03 Отформатируйте предыдущей запрос - выведите день недели для этой даты.
      Используйте документацию My SQL */

-- Weekday in Russian
SET
lc_time_names = 'ru_RU';
SELECT
    DATE_ADD(NOW(), INTERVAL 51 DAY) AS future_date,
    DAYNAME(DATE_ADD(NOW(), INTERVAL 51 DAY)) AS weekday_name;

/* 04 Подключитесь к базе данных northwind
    Выведите столбец с исходной датой создания транзакции
    transaction_created_date из таблицы inventory_transactions,
    а также столбец полученный прибавлением 3 часов к этой дате */

SELECT
    transaction_created_date,
    DATE_ADD(transaction_created_date, INTERVAL 3 HOUR
    ) AS transaction_plus_3_hours
FROM northwind.inventory_transactions;

/* 05 Выведите столбец с текстом  'Клиент с id <customer_id>
сделал заказ <order_date>'    из таблицы orders
Запрос написать двумя способами
	- с использованием неявных преобразований
    - а также с указанием изменения типа данных для столбца customer_id
Внимание В MySQL функция CAST не принимает VARCHAR в качестве параметра
для длины. Вместо этого, нужно использовать CHAR для указания длины. */
-- Variant 1 - with implicit conversions
SELECT
    CONCAT('Клиент с id ', customer_id, ' сделал заказ ', order_date
    ) AS order_info
FROM northwind.orders;
-- Variant 2 - with explicit conversions
SELECT
    CONCAT(
        'Клиент с id ',
        CAST(customer_id AS CHAR),
        ' сделал заказ ',
        CAST(order_date AS CHAR)
    ) AS order_info
FROM northwind.orders;

