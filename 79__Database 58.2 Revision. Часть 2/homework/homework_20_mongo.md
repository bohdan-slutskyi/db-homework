Pаботаем с коллекцией ich.sample_data.restaurants

> Источник: `../../63__Database 46.2 MongoDB: Создание и наполнение коллекций. Агрегация. Часть 2/materials/theory_04__aggregation_all_stages.md` — стадии `$match`, `$unwind`, `$group`, `$sort`, `$limit`, `$project`;
> `../../63__Database 46.2 MongoDB: Создание и наполнение коллекций. Агрегация. Часть 2/materials/theory_05__some_aggregation_functions.md` — `$avg`;
> `../../79__Database 58.2 Revision. Часть 2/materials/theory_03__regex.md` — `$regex` и `$options`.

/* 1. Найти рестораны на borough 'Staten Island' в названии которых есть слово pizza
(Pizza и PIZZA тоже считаются) */

```python
result = client['sample_data']['restaurants'].aggregate([
    {
        '$match': {
            'borough': 'Staten Island',
            'name': {
                '$regex': 'pizza',
                '$options': 'i'
            }
        }
    }
])
```

Проверка в MongoDB Compass: найдено `67` ресторанов. Первые в выдаче:
`Pizza D'Oro`, `Salvatore And Lloyd'S Pizza`, `Village Maria Pizza Ii`.


/* 2. Выведите названия 5 лучших по среднему значению отзывов ( $avg: "$grades.score") */

```python
result = client['sample_data']['restaurants'].aggregate([
    {
        '$unwind': '$grades'
    },
    {
        '$group': {
            '_id': '$_id',
            'name': {'$first': '$name'},
            'average_score': {'$avg': '$grades.score'}
        }
    },
    {
        '$sort': {
            'average_score': -1
        }
    },
    {
        '$limit': 5
    },
    {
        '$project': {
            '_id': 0,
            'name': 1,
            'average_score': 1
        }
    }
])
```

Проверка в MongoDB Compass:

- `Juice It Health Bar` — средний балл `75`;
- `Golden Dragon Cuisine` — средний балл `73`;
- `Palombo Pastry Shop` — средний балл `69`;
- `Chelsea'S Juice Factory` — средний балл `69`;
- `Go Go Curry` — средний балл `65`.
