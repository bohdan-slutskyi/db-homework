/* 1. Из коллекции Atlas: sample_airbnb.listingsAndReviews найдите среднюю цену за сутки проживания на Гавайских островах. Островов несколько, поэтому либо используем {'address.location': {$geoWithin: { $centerSphere …. , либо перечисляем все возможные острова в поле market.
Подсказка - нам понадобится 2 этапа агрегации : $match и $group
*/

Фильтруем объявления внутри круга радиусом `0.0847` радиана вокруг Гавайев,
затем вычисляем среднюю цену поля `price`.

```python
result = client['sample_airbnb']['listingsAndReviews'].aggregate([
    {
        '$match': {
            'address.location': {
                '$geoWithin': {
                    '$centerSphere': [[-157.8583, 21.3069], 0.0847]
                }
            }
        }
    },
    {
        '$group': {
            '_id': None,
            'average_price_per_night': {'$avg': '$price'}
        }
    }
])
```

Проверка в MongoDB Compass: `average_price_per_night = 231.4853420195439739413680781758958`.

> Источник: `../materials/theory_07__$geoWithin.md` — `$geoWithin` и `$centerSphere`; `../../63__Database 46.2 MongoDB: Создание и наполнение коллекций. Агрегация. Часть 2/materials/theory_05__some_aggregation_functions.md` — `$group` и `$avg`.

/* 2.1. Подсчитайте в коллекции Atlas: sample_mflix.movies,
 сколько фильмов имеют imdb рейтинг выше 8 и выходили в период с 2015 до 2023 года.*/

Оставляем фильмы с рейтингом выше `8` и годом выпуска от `2015` до `2023`
включительно, затем считаем документы.

```python
result = client['sample_mflix']['movies'].aggregate([
    {
        '$match': {
            'imdb.rating': {'$gt': 8},
            'year': {'$gte': 2015, '$lte': 2023}
        }
    },
    {
        '$group': {
            '_id': None,
            'films_count': {'$sum': 1}
        }
    }
])
```

Проверка в MongoDB Compass: `films_count = 53`.

> Источник: `../../63__Database 46.2 MongoDB: Создание и наполнение коллекций. Агрегация. Часть 2/materials/theory_05__some_aggregation_functions.md` — `$group` и `$sum` для подсчёта документов.

/* 2.2. Какой из фильмов, вышедших в период с 2015 по 2023 имеет самый высокий рейтинг? */

Фильтруем фильмы за указанный период и оставляем только числовые значения
`imdb.rating`: в коллекции встречаются пустые строки. Затем сортируем по
рейтингу по убыванию и оставляем один фильм с максимальным рейтингом.

```python
result = client['sample_mflix']['movies'].aggregate([
    {
        '$match': {
            'year': {'$gte': 2015, '$lte': 2023},
            'imdb.rating': {'$type': 'double'}
        }
    },
    {'$sort': {'imdb.rating': -1}},
    {'$limit': 1},
    {
        '$project': {
            '_id': 0,
            'title': 1,
            'year': 1,
            'imdb.rating': 1
        }
    }
])
```

Проверка в MongoDB Compass: `A Brave Heart: The Lizzie Velasquez Story`,
`year = 2015`, `imdb.rating = 9.4`.

> Источник: `../../63__Database 46.2 MongoDB: Создание и наполнение коллекций. Агрегация. Часть 2/materials/theory_04__aggregation_all_stages.md` — стадии `$match`, `$sort`, `$limit` и `$project`.
