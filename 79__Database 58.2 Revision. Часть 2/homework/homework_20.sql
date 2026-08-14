-- 1. Работаем с базой данных sakila.

-- Источник: ../../06__Database 4.1 Условные конструкции: операторы CASE, IF/materials/theory_01__CASE_IF.md — CASE;
-- ../../18__Database 13.1 Агрегирующие функции. Оператор Group BY/materials/theory_02__GROUP_BY__HAVING.md — GROUP BY;
-- ../../23__Database 16.2 Операторы JOIN и UNION/materials/theory_05__UNION_&_JOIN.md — JOIN;
-- ../../34__Database 25.1 Оконные функции. Общие концепции/materials/theory_02__type_of_windows_functions.md — COUNT() OVER;
-- ../../11__Database 7.2 Особенности работы с датой и временем/materials/theory_04__date_time_fucntions.md — DATE_FORMAT().

/* 2. Вывести названия фильмов с расшифровкой рейтинга для каждого.
 В таблице film хранятся годы рейтингов:
  G – Все возрастные категории.
  PG – Рекомендуется контроль родителей.
  PG-13 – Осторожно, для детей до 13 лет.
  R – Ограничено. Для детей до 17 лет требуется сопровождение взрослого.
  NC-17 - Только для зрителей старше 17 лет.

Нужно воспользоваться оператором case чтобы определить для каждого кода условие,
по которому будет выводится его развернутое описание (1 предложение). */

SELECT
    title,
    rating,
    CASE rating
        WHEN 'G' THEN 'Все возрастные категории.'
        WHEN 'PG' THEN 'Рекомендуется контроль родителей.'
        WHEN 'PG-13' THEN 'Осторожно, для детей до 13 лет.'
        WHEN 'R' THEN 'Ограничено: для детей до 17 лет требуется сопровождение взрослого.'
        WHEN 'NC-17' THEN 'Только для зрителей старше 17 лет.'
    END AS rating_description
FROM film;

/* 3. Выведите количество фильмов в каждой категории рейтинга.
Используем group by. */

SELECT
    rating,
    COUNT(*) AS films_count
FROM film
GROUP BY rating
ORDER BY rating;

/* 4. Используя оконные функции и partition by, выведите
список названий фильмов, рейтинг и количество фильмов в каждом рейтинге.
Объясните, чем отличаются результаты предыдущего запроса и запроса в этой задаче. */

SELECT
    title,
    rating,
    COUNT(*) OVER (PARTITION BY rating) AS films_count_in_rating
FROM film
ORDER BY rating, title;

-- В задании 3 GROUP BY объединяет фильмы в группы, поэтому в результате одна
-- строка на рейтинг. В задании 4 оконная функция не объединяет строки: каждый
-- фильм остаётся в результате, а количество фильмов его рейтинга повторяется
-- для всех фильмов этой группы.

/* 5. Изучите таблицы payment и customer. Выведите список всех платежей с указанием
имени и фамилии каждого заказчика, датой платежа и суммой. */

SELECT
    c.first_name,
    c.last_name,
    p.payment_date,
    p.amount
FROM payment AS p
INNER JOIN customer AS c
    ON p.customer_id = c.customer_id
ORDER BY p.payment_date;

/* 6. Поменяйте предыдущий запрос так, чтобы дата выводилась в формате
“число, название месяца, год” (без времени). */

SELECT
    c.first_name,
    c.last_name,
    p.amount,
    DATE_FORMAT(p.payment_date, '%d, %M, %Y') AS payment_date
FROM payment AS p
INNER JOIN customer AS c
    ON p.customer_id = c.customer_id
ORDER BY p.payment_date;
