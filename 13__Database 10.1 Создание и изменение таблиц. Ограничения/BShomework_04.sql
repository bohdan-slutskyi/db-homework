-- 01 Подключитесь к своей базе данных созданной на уроке.
USE your_db;

/* 02 Создайте таблицу, которая отражает погоду в Вашем городе за последние 5 дней и включает следующее столбцы.
Id - первичный ключ, заполняется автоматически
Дата - не может быть пропуском
Дневная температура - целое число, принимает значения от -30 до 30
Ночная температура - целое число, принимает значения от -30 до 30
Скорость ветра - подумайте какой тип данных и ограничения необходимы для этого столбца. */

-- 03 Заполните таблицу 5 строками - за последние 5 дней.



-- 04 Увеличьте значения ночной температуры на градус если скорость ветра не превышала 3 м/с.



/* 05 Средняя суточная температура - среднее арифметическое между ночной и дневной температурами
Столбец на основе скорости ветра - если скорость ветра не превышала 2 м/с то значение ‘штиль’,
от 2 включительно до 5 - ‘умеренный ветер’,
в остальных случаях - ‘сильный ветер’. */


-- 06 Отформатируйте стиль написания запросов.

-- 07 Сохраните запросы в виде файла с расширением .sql и загрузите на платформу.

-- Databases 2025: Homework 4
-- Комментарий:
-- В исходном задании было пересечение условий для скорости ветра:
-- "не превышала 2 м/с" и "от 2 включительно до 5".
-- Поэтому в решении используется исправленный вариант:
-- wind_speed < 2           -> 'штиль'
-- wind_speed BETWEEN 2 AND 5 -> 'умеренный ветер'
-- wind_speed > 5           -> 'сильный ветер'

-- 1. Подключение к своей базе данных
USE `060326_ptm_SLU`;

-- 2. Создание таблицы погоды
DROP TABLE IF EXISTS weather;

CREATE TABLE IF NOT EXISTS weather (
    id INT AUTO_INCREMENT PRIMARY KEY,
    weather_date DATE NOT NULL,
    day_temperature INT CHECK (day_temperature BETWEEN -30 AND 30),
    night_temperature INT CHECK (night_temperature BETWEEN -30 AND 30),
    wind_speed DECIMAL(3, 1) NOT NULL CHECK (wind_speed >= 0)
);

-- 3. Заполнение таблицы 5 строками за последние 5 дней
INSERT INTO weather (weather_date, day_temperature, night_temperature, wind_speed)
VALUES
    (CURDATE() - INTERVAL 4 DAY, 12, 5, 1.5),
    (CURDATE() - INTERVAL 3 DAY, 10, 3, 2.0),
    (CURDATE() - INTERVAL 2 DAY, 8, 1, 3.0),
    (CURDATE() - INTERVAL 1 DAY, 6, 0, 4.5),
    (CURDATE(), 9, 2, 6.2);

-- Проверка данных
SELECT *
FROM weather;

-- 4. Увеличение ночной температуры на 1 градус,
-- если скорость ветра не превышала 3 м/с
UPDATE weather
SET night_temperature = night_temperature + 1
WHERE wind_speed <= 3;

-- Проверка после обновления
SELECT *
FROM weather;

-- 5. Создание представления
DROP VIEW IF EXISTS weather_view;

CREATE VIEW weather_view AS
SELECT
    id,
    weather_date,
    day_temperature,
    night_temperature,
    wind_speed,
    round((day_temperature + night_temperature) / 2, 1) AS average_daily_temperature,
    CASE
        WHEN wind_speed < 2 THEN 'штиль'
        WHEN wind_speed BETWEEN 2 AND 5 THEN 'умеренный ветер'
        ELSE 'сильный ветер'
    END AS wind_description
FROM weather;

-- Проверка представления
SELECT *
FROM weather_view;