CREATE DATABASE IF NOT EXISTS 060326_ptm_SLU;
USE 060326_ptm_SLU;

/* Работайте со своей ранее созданной БД */


/* 1. Создайте хранимую процедуру get_department_id, которая
    принимает id сотрудника (IN-параметр), и возвращает id департамента
    (где работает сотрудник) через OUT-параметр. */

-- Удаляем старую версию процедуры, чтобы файл можно было запускать повторно.
DROP PROCEDURE IF EXISTS get_department_id;

DELIMITER //

CREATE PROCEDURE get_department_id(
    IN emp_id INT,      -- IN-параметр: сюда передаём id сотрудника
    OUT dept_id INT     -- OUT-параметр: сюда процедура запишет id департамента
)
BEGIN
    -- Находим department_id сотрудника по его employee_id.
    -- Результат сразу записываем в OUT-параметр dept_id.
    SELECT department_id
    INTO dept_id
    FROM employees
    WHERE employee_id = emp_id;
END //

DELIMITER ;

-- Проверка процедуры:
CALL get_department_id(101, @dept);
SELECT @dept AS department_id;


/* 2. Создайте хранимую процедуру get_employee_age, которая
   принимает id сотрудника (IN-параметр)
   и возвращает его возраст через OUT-параметр. */

-- Удаляем старую версию процедуры, чтобы файл можно было запускать повторно.
DROP PROCEDURE IF EXISTS get_employee_age;

DELIMITER //

CREATE PROCEDURE get_employee_age(
    IN emp_id INT,      -- IN-параметр: сюда передаём id сотрудника
    OUT emp_age INT     -- OUT-параметр: сюда процедура запишет возраст сотрудника
)
BEGIN
    -- В нашей таблице employees уже есть готовая колонка age.
    -- Поэтому просто берём age сотрудника и записываем в OUT-параметр.
    SELECT age
    INTO emp_age
    FROM employees
    WHERE employee_id = emp_id;
END //

DELIMITER ;

-- Проверка процедуры:
CALL get_employee_age(101, @age);
SELECT @age AS employee_age;


/* 3. Создайте хранимую процедуру increase_salary, которая
   принимает зарплату сотрудника (INOUT-параметр) и уменьшает ее на 10%. */

-- Удаляем старую версию процедуры, чтобы файл можно было запускать повторно.
DROP PROCEDURE IF EXISTS increase_salary;

DELIMITER //

CREATE PROCEDURE increase_salary(
    INOUT salary DECIMAL(10, 2)   -- INOUT: получаем зарплату, меняем её и возвращаем обратно
)
BEGIN
    -- Уменьшаем переданное значение зарплаты на 10%.
    SET salary = salary * 0.9;
END //

DELIMITER ;

-- Проверка процедуры:
-- Берём реальную зарплату сотрудника из таблицы employees.
-- Это значение попадёт во внешнюю переменную @sal.
-- Затем INOUT-процедура уменьшит это значение на 10% и вернёт обратно в @sal.
-- Важно: сама таблица employees здесь не изменяется, меняется только переменная @sal.
SELECT salary
INTO @sal
FROM employees
WHERE employee_id = 101;

CALL increase_salary(@sal);
SELECT @sal AS decreased_salary;