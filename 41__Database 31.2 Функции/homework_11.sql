CREATE DATABASE IF NOT EXISTS 060326_ptm_SLU;
USE 060326_ptm_SLU;
/* 1. Расчёт площади круга
Создайте функцию для расчета площади круга, если известен его радиус.
Используйте формулу
Где:
S — площадь круга,
r — радиус круга,
π ≈ 3.14159 */

DROP FUNCTION IF EXISTS circle_area;

CREATE FUNCTION circle_area(radius DECIMAL(10,5))
RETURNS DECIMAL(10,5)
DETERMINISTIC
RETURN PI() * radius * radius;


SELECT circle_area(1); -- 3.141590


/* 2. Расчёт гипотенузы треугольника
Создайте функцию для расчета гипотенузы треугольника, если известны длины его катетов.
Используйте формулу c = SQRT(a * a + b * b)
Где:
c — длина гипотенузы треугольника,
a, b — длины его катетов */

DROP FUNCTION IF EXISTS hypotenuse;

CREATE FUNCTION hypotenuse(a DECIMAL(10,2), b DECIMAL(10,2))
RETURNS DECIMAL(10,2)
DETERMINISTIC
RETURN SQRT(a * a + b * b);

SELECT hypotenuse(3, 4);  -- 5