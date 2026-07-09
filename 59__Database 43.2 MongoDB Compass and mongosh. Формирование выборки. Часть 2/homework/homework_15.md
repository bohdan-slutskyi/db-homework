/* 1. Коллекция imdb : Используя оператор $size, найдите фильмы,
написанные 3 сценаристами (writers) и снятые 2 режиссерами (directors) */

```python
client = MongoClient('mongodb://localhost:27017/')

result = client['ich']['imdb'].aggregate([
    {
        '$match': {
            'writers': {
                '$size': 3
            },
            'directors': {
                '$size': 2
            }
        }
    }, {
        '$project': {
            '_id': 0,
            'title': 1,
            'year': 1,
            'writers': 1,
            'directors': 1
        }
    }
])
```

/* 2. Коллекция bookings: Найдите адрес нахождения автомобиля с vin WME4530421Y135045
по самой последней дате (и времени) final_date */

```python
client = MongoClient('mongodb://localhost:27017/')

result = client['ich']['bookings'].aggregate([
    {
        '$match': {
            'vin': 'WME4530421Y135045'
        }
    }, {
        '$sort': {
            'final_date': -1
        }
    }, {
        '$limit': 1
    }, {
        '$project': {
            '_id': 0,
            'final_address': 1,
            'vin': 1,
            'plate': 1,
            'final_date': 1
        }
    }
])
```

/* 3. Коллекция bookings: подсчитайте, у скольких автомобилей
при окончании аренды закончилось топливо (final_fuel) */

```python
client = MongoClient('mongodb://localhost:27017/')

result = client['ich']['bookings'].aggregate([
    {
        '$match': {
            'final_fuel': 0
        }
    }, {
        '$count': 'count'
    }
])
# confirmed result: 30
```

/* 4. Коллекция bookings: найдите номерной знак и vin номер авто,
с самым большим пробегом (distance) */

```python
client = MongoClient('mongodb://localhost:27017/')

result = client['ich']['bookings'].aggregate([
    {
        '$sort': {
            'distance': -1
        }
    }, {
        '$limit': 1
    }, {
        '$project': {
            '_id': 0,
            'plate': 1,
            'vin': 1,
            'distance': 1
        }
    }
])
```

/* 5. Коллекция imdb. Найдите фильм с участием "Brad Pitt"
с самым высоким рейтингом (imdb.rating) */

```python
client = MongoClient('mongodb://localhost:27017/')

result = client['ich']['imdb'].aggregate([
    {
        '$match': {
            'cast': 'Brad Pitt',
            'imdb.rating': {
                '$type': 'double'
            }
        }
    }, {
        '$sort': {
            'imdb.rating': -1
        }
    }, {
        '$limit': 1
    }, {
        '$project': {
            '_id': 0,
            'title': 1,
            'year': 1,
            'cast': 1,
            'imdb': 1
        }
    }
])
```
