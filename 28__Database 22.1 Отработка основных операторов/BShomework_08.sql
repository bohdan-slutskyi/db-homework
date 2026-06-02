-- 1. Найдите все записи таблицы Printer для цветных принтеров.

select * from Printer where color = 'y';

/* 2. Найдите номера моделей и цены всех имеющихся в продаже продуктов (любого типа)
   производителя B (латинская буква).
   Вывести: model, price. */

SELECT p.model, prices.price
FROM product AS p
JOIN (
    SELECT model, price FROM pc
    UNION
    SELECT model, price FROM laptop
    UNION
    SELECT model, price FROM printer
) AS prices
    ON p.model = prices.model
WHERE p.maker = 'B';

-- 3. Найдите производителя, выпускающего ПК, но при этом не выпускающего ПК-блокноты (Laptop)

SELECT DISTINCT p.maker           -- получить производителя
FROM product AS p                 -- из таблицы product
WHERE p.type = 'PC'               -- оставить только производителей PC
  AND p.maker NOT IN (            -- исключить тех, кто выпускает Laptop
      SELECT maker                -- найти производителей Laptop
      FROM product                -- в той же таблице product
      WHERE type = 'Laptop'       -- только тип Laptop
  );


-- 4. Найдите производителей ПК с процессором не менее 450 Мгц. Вывести: Maker.
SELECT DISTINCT p.maker
FROM product AS p
JOIN pc AS pc ON p.model = pc.model
WHERE p.type = 'PC' AND pc.speed >= 450;

-- 5. Найдите среднюю скорость всех ПК.
SELECT AVG(speed) AS average_speed
FROM pc;

/* 6. Для каждого производителя, имеющего модели в таблице Laptop,
   найдите средний размер экрана выпускаемых им Laptop.
   Вывести: maker, средний размер экрана. */
SELECT p.maker, AVG(l.screen) AS average_screen_size
FROM product AS p
JOIN laptop AS l ON p.model = l.model
WHERE p.type = 'Laptop'
GROUP BY p.maker;
