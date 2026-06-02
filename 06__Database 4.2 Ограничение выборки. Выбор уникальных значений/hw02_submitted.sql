/*
Homework 01
Topic: SELECT, FROM, WHERE
Database: northwind
*/

/* 1. Выберите все строки из таблицы suppliers.
   Предварительно подключитесь к базе данных northwind. */

-- ustanavlivaem aktivnuyu bazu dannyh
USE northwind;

SELECT
    id,
    company,
    last_name,
    first_name,
    email_address,
    job_title,
    business_phone,
    home_phone,
    mobile_phone,
    fax_number,
    address,
    city,
    state_province,
    zip_postal_code,
    country_region,
    web_page,
    notes,
    attachments
FROM
    suppliers;

-- 2. Выберите только те строки из таблицы suppliers,
-- где company имеет значение Supplier A.

SELECT company
FROM
    suppliers
WHERE
    company = 'Supplier A';

-- 3. Выберите все строки из таблицы purchase_orders.

SELECT
    id,
    supplier_id,
    created_by,
    submitted_date,
    creation_date,
    status_id,
    expected_date,
    shipping_fee,
    taxes,
    payment_date,
    payment_amount,
    payment_method,
    notes,
    approved_by,
    approved_date,
    submitted_by
FROM
    purchase_orders;

-- 4. Выберите только те строки из таблицы purchase_orders,
-- где supplier_id = 2.

SELECT
    id,
    supplier_id,
    created_by,
    submitted_date,
    creation_date,
    status_id,
    expected_date,
    shipping_fee,
    taxes,
    payment_date,
    payment_amount,
    payment_method,
    notes,
    approved_by,
    approved_date,
    submitted_by
FROM
    purchase_orders
WHERE
    supplier_id = 2;

/* 5. Выберите supplier_id и shipping_fee из purchase_orders,
   где created_by равно 1 и supplier_id равен 5.
   Объясните полученный результат. */

SELECT
    supplier_id,
    shipping_fee
FROM
    purchase_orders
WHERE
    created_by = 1
    AND supplier_id = 5;

/* Результат пустой, так как в таблице purchase_orders отсутствуют записи,
   которые одновременно удовлетворяют обоим условиям:
   created_by = 1 и supplier_id = 5. */

/* 6. Выберите last_name и first_name из таблицы employees,
   где address имеет значение 123 2nd Avenue или 123 8th Avenue.
   Напишите запрос двумя способами: с применением оператора OR и
   оператора IN. */

/* Вариант 1 - через OR */
SELECT
    last_name,
    first_name
FROM
    employees
WHERE
    address = '123 2nd Avenue'
    OR address = '123 8th Avenue';

/* Вариант 2 - через IN */
SELECT
    last_name,
    first_name
FROM
    employees
WHERE
    address IN ('123 2nd Avenue', '123 8th Avenue');

-- 7. Выведите все имена сотрудников, которые содержат
-- английскую букву p в середине фамилии.

SELECT first_name
FROM
    employees
WHERE
    last_name LIKE '_%p%_';

-- 8. Выберите все строки из таблицы orders,
-- где нет информации о shipper_id.

SELECT
    id,
    employee_id,
    customer_id,
    order_date,
    shipped_date,
    shipper_id,
    ship_name,
    ship_address,
    ship_city,
    ship_state_province,
    ship_zip_postal_code,
    ship_country_region,
    shipping_fee,
    taxes,
    payment_type,
    paid_date,
    notes,
    tax_rate,
    tax_status_id,
    status_id
FROM
    orders
WHERE
    shipper_id IS NULL;

-- 9. Отформатируйте стиль написания запросов.

-- 10. Сохраните запросы в виде файла с расширением .sql
-- и загрузите на платформу.
