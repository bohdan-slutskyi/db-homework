# Домашнее задание 16. Агрегация MongoDB

> Исходное задание: [LMS — Databases 2025: Домашнее задание 16](https://lms.itcareerhub.de/mod/assign/view.php?id=14684).
>
> Источник: `db-course/63__Database 46.2 MongoDB: Создание и наполнение коллекций. Агрегация. Часть 2/materials/theory_04__aggregation_all_stages.md` — стадии `$match`, `$group`, `$count`, `$sort`, `$limit` и `$project`.
>
> Источник: `db-course/63__Database 46.2 MongoDB: Создание и наполнение коллекций. Агрегация. Часть 2/materials/theory_05__some_aggregation_functions.md` — функции `$sum` и `$avg`.
>
> Источник: `db-course/62__Database 46.1 MongoDB: Создание и наполнение коллекций. Агрегация. Часть 1/materials/theory_01__add_or_create_documents.md` — `insertMany()`.

## 1. Найти средний возраст в `ich.US_Adult_Income`

**Полная агрегация после экспорта в Python:**

```python
result = client['ich']['US_Adult_Income'].aggregate([
    {
        '$group': {
            '_id': None,
            'average_age': {
                '$avg': '$age'
            }
        }
    }
])
```

## 2. Создать и заполнить коллекцию `060326-ptm_orders_slutskyi`

```javascript
db["060326-ptm_orders_slutskyi"].insertMany([
  { id: 1, customer: "Olga", product: "Apple", amount: 15.55, city: "Berlin" },
  { id: 2, customer: "Anna", product: "Apple", amount: 10.05, city: "Madrid" },
  { id: 3, customer: "Olga", product: "Kiwi", amount: 9.6, city: "Berlin" },
  { id: 4, customer: "Anton", product: "Apple", amount: 20, city: "Roma" },
  { id: 5, customer: "Olga", product: "Banana", amount: 8, city: "Madrid" },
  { id: 6, customer: "Petr", product: "Orange", amount: 18.3, city: "Paris" }
])
```

## 3. Найти общее количество покупок

**Полная агрегация после экспорта в Python:**

```python
result = client['ich_edit']['060326-ptm_orders_slutskyi'].aggregate([
    {
        '$count': 'total'
    }
])
```

## 4. Найти, сколько раз были куплены яблоки

**Полная агрегация после экспорта в Python:**

```python
result = client['ich_edit']['060326-ptm_orders_slutskyi'].aggregate([
    {
        '$match': {
            'product': 'Apple'
        }
    },
    {
        '$count': 'total'
    }
])
```

## 5. Вывести идентификаторы трёх самых дорогих покупок

**Полная агрегация после экспорта в Python:**

```python
result = client['ich_edit']['060326-ptm_orders_slutskyi'].aggregate([
    {
        '$sort': {
            'amount': -1
        }
    },
    {
        '$limit': 3
    },
    {
        '$project': {
            '_id': 0,
            'id': 1,
            'amount': 1
        }
    }
])
```

## 6. Найти количество покупок, совершённых в Берлине

**Полная агрегация после экспорта в Python:**

```python
result = client['ich_edit']['060326-ptm_orders_slutskyi'].aggregate([
    {
        '$match': {
            'city': 'Berlin'
        }
    },
    {
        '$count': 'total'
    }
])
```

## 7. Найти количество покупок яблок в Берлине и Мадриде

**Полная агрегация после экспорта в Python:**

```python
result = client['ich_edit']['060326-ptm_orders_slutskyi'].aggregate([
    {
        '$match': {
            'product': 'Apple',
            'city': {
                '$in': [
                    'Berlin',
                    'Madrid'
                ]
            }
        }
    },
    {
        '$count': 'total'
    }
])
```

## 8. Найти, сколько было потрачено каждым покупателем

**Полная агрегация после экспорта в Python:**

```python
result = client['ich_edit']['060326-ptm_orders_slutskyi'].aggregate([
    {
        '$group': {
            '_id': '$customer',
            'total': {
                '$sum': '$amount'
            }
        }
    }
])
```

## 9. Найти города, в которых Ольга совершала покупки

**Полная агрегация после экспорта в Python:**

```python
result = client['ich_edit']['060326-ptm_orders_slutskyi'].aggregate([
    {
        '$match': {
            'customer': 'Olga'
        }
    },
    {
        '$group': {
            '_id': '$city'
        }
    }
])
```
