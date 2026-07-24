/* 1. Тестовая коллекция в mongo atlas  sample_mflix.theaters
Найти все кинотеатры в Калифорнии ("CA") и посчитать их количество */

Фильтруем кинотеатры по полю
`location.address.state: "CA"`, затем передаём число найденных документов в
поле `count`.

```javascript
db.theaters.aggregate([
  { $match: { "location.address.state": "CA" } },
  { $count: "count" }
]);
```

Найдено `169` кинотеатров в Калифорнии.

> Источник: ../../63__Database 46.2 MongoDB: Создание и наполнение коллекций. Агрегация. Часть 2/materials/theory_04__aggregation_all_stages.md — стадии `$match` и `$count`

/* 2. Тестовая коллекция в mongo atlas  sample_airbnb.listingsAndReviews
Найти недвижимость с самым большим количеством спален (bedrooms) и напишите ее название */

Сортируем объявления по `bedrooms` по убыванию, оставляем
первый документ и выводим его название вместе с количеством спален.

```javascript
db.listingsAndReviews.aggregate([
  { $sort: { bedrooms: -1 } },
  { $limit: 1 },
  { $project: { _id: 0, name: 1, bedrooms: 1 } }
]);
```

Итог - `Venue Hotel Old City` — `20` спален.

> Источник: ../../63__Database 46.2 MongoDB: Создание и наполнение коллекций. Агрегация. Часть 2/materials/theory_04__aggregation_all_stages.md — стадии `$sort` и `$limit`

/* 3. Тестовая коллекция в mongo atlas  sample_airbnb.listingsAndReviews
Найти недвижимость с самым высоким рейтингом  review_scores_rating при минимальном количестве отзывов 50 (number_of_reviews) и напишите ее название */

отбераем объявления с `number_of_reviews` не меньше `50`,
отсортируем по `review_scores.review_scores_rating` по убыванию, оставляем
первое и выводим название, рейтинг и число отзывов.

```javascript
db.listingsAndReviews.aggregate([
  { $match: { number_of_reviews: { $gte: 50 } } },
  { $sort: { "review_scores.review_scores_rating": -1 } },
  { $limit: 1 },
  {
    $project: {
      _id: 0,
      name: 1,
      review_scores_rating: "$review_scores.review_scores_rating",
      number_of_reviews: 1
    }
  }
]);
```

В итоге - `Sydney Hyde Park City Apartment (checkin from 6am)` — рейтинг
`100`, количество отзывов `109`.

> Источник: ../../63__Database 46.2 MongoDB: Создание и наполнение коллекций. Агрегация. Часть 2/materials/theory_04__aggregation_all_stages.md — стадии `$match`, `$sort`, `$limit` и `$project`
