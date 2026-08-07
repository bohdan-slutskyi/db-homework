// Из базы данных ich работаем с коллекцией ich.Spotify_Youtube:

/* 1. Найдите трек с наивысшими показателями Danceability и Energy (в сумме) */

Создаём поле с суммой `Danceability` и `Energy`, сортируем по нему по убыванию
и оставляем один трек с максимальным результатом.

```python
result = client['ich']['Spotify_Youtube'].aggregate([
    {
        '$set': {
            'danceability_energy_total': {
                '$add': ['$Danceability', '$Energy']
            }
        }
    },
    {
        '$sort': {
            'danceability_energy_total': -1
        }
    },
    {
        '$limit': 1
    },
    {
        '$project': {
            '_id': 0,
            'Track': 1,
            'Artist': 1,
            'Danceability': 1,
            'Energy': 1,
            'danceability_energy_total': 1
        }
    }
])
```

Проверка в MongoDB Compass: Miranda! — `Yo Te Diré`; Danceability = `0.917`,
Energy = `0.98`, их сумма = `1.897`.

> Источник: `../materials/theory_06__$set_vs_$addField.md` — вычисляемое поле через `$set`; `../../55__Database 40.2 Знакомство с mongoDB. Часть 2/materials/theory_08__math_operations.md` — `$add`; `../../63__Database 46.2 MongoDB: Создание и наполнение коллекций. Агрегация. Часть 2/materials/theory_04__aggregation_all_stages.md` — `$sort`, `$limit`, `$project`.

/* 2. У какого трека (но не compilation) самая большая длительность? */

Исключаем альбомы типа `compilation`, сортируем оставшиеся треки по
`Duration_ms` по убыванию и оставляем первый результат.

```python
result = client['ich']['Spotify_Youtube'].aggregate([
    {
        '$match': {
            'Album_type': {
                '$ne': 'compilation'
            }
        }
    },
    {
        '$sort': {
            'Duration_ms': -1
        }
    },
    {
        '$limit': 1
    },
    {
        '$project': {
            '_id': 0,
            'Track': 1,
            'Artist': 1,
            'Album': 1,
            'Album_type': 1,
            'Duration_ms': 1
        }
    }
])
```

Проверка в MongoDB Compass: Ocean Waves For Sleep — `Ocean Waves for Sleep`
из сингла `Ocean Waves`; Duration_ms = `4120258`.

> Источник: `../../55__Database 40.2 Знакомство с mongoDB. Часть 2/materials/theory_07__logical_operations.md` — `$ne`; `../../63__Database 46.2 MongoDB: Создание и наполнение коллекций. Агрегация. Часть 2/materials/theory_04__aggregation_all_stages.md` — `$match`, `$sort`, `$limit`, `$project`.

/* 3. В каком одном альбоме самое большее количество треков? */

Группируем документы по названию альбома, считаем треки в каждой группе,
сортируем по количеству по убыванию и оставляем один альбом.

```python
result = client['ich']['Spotify_Youtube'].aggregate([
    {
        '$group': {
            '_id': '$Album',
            'tracks_count': {
                '$sum': 1
            }
        }
    },
    {
        '$sort': {
            'tracks_count': -1
        }
    },
    {
        '$limit': 1
    },
    {
        '$project': {
            '_id': 0,
            'album': '$_id',
            'tracks_count': 1
        }
    }
])
```

Проверка в MongoDB Compass: альбом `Greatest Hits`, `30` треков.

> Источник: `../../63__Database 46.2 MongoDB: Создание и наполнение коллекций. Агрегация. Часть 2/materials/theory_04__aggregation_all_stages.md` — `$group`, `$sort`, `$limit`, `$project`; `../../63__Database 46.2 MongoDB: Создание и наполнение коллекций. Агрегация. Часть 2/materials/theory_05__some_aggregation_functions.md` — `$sum`.

/* 4. Сколько просмотров видео на youtube у трека
с самым высоким количеством прослушиваний на spotify (Stream)? */

Сортируем треки по числу прослушиваний `Stream` по убыванию, оставляем один
трек и выводим число его просмотров `Views`.

```python
result = client['ich']['Spotify_Youtube'].aggregate([
    {
        '$sort': {
            'Stream': -1
        }
    },
    {
        '$limit': 1
    },
    {
        '$project': {
            '_id': 0,
            'Track': 1,
            'Artist': 1,
            'Stream': 1,
            'Views': 1
        }
    }
])
```

Проверка в MongoDB Compass: The Weeknd — `Blinding Lights`; Stream =
`3386520288`, Views = `674164500`.

> Источник: `../../63__Database 46.2 MongoDB: Создание и наполнение коллекций. Агрегация. Часть 2/materials/theory_04__aggregation_all_stages.md` — `$sort`, `$limit`, `$project`.

/* 5. Экспортируйте 20 самых популярных (прослушивания или просмотры) треков
по версиям youtube и spotify и импортируйте в базу ich_edit их
с именами top20youtube и top20spotify, и добавьте им свои имена для уникальности. */

Сортируем треки по просмотрам или прослушиваниям, оставляем первые `20` и
сохраняем результат в уникальные коллекции базы `ich_edit`.

```python
youtube_result = client['ich']['Spotify_Youtube'].aggregate([
    {
        '$sort': {
            'Views': -1
        }
    },
    {
        '$limit': 20
    },
    {
        '$out': {
            'db': 'ich_edit',
            'coll': 'top20youtube_bohdan_slutskyi'
        }
    }
])

spotify_result = client['ich']['Spotify_Youtube'].aggregate([
    {
        '$sort': {
            'Stream': -1
        }
    },
    {
        '$limit': 20
    },
    {
        '$out': {
            'db': 'ich_edit',
            'coll': 'top20spotify_bohdan_slutskyi'
        }
    }
])
```

> Источник: `../../63__Database 46.2 MongoDB: Создание и наполнение коллекций. Агрегация. Часть 2/materials/theory_04__aggregation_all_stages.md` — `$out`, `$sort`, `$limit`.
