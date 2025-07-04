
# 📦 Структуры данных (массивы) в Python

В Python есть несколько встроенных **структур данных (массивов)**: `list`, `tuple`, `dict`, `set`. Каждая служит своей цели.

---

## 🔹 1. `list` (список)
Список — **изменяемая** упорядоченная коллекция элементов.

```python
numbers = [1, 2, 3]
```

**Особенности:**
- Поддерживает дубли.
- Можно изменять: добавлять, удалять, изменять элементы.
- Поддерживает индексирование и срезы.

**Встроенный тип:** `list`  
**Типизация (Python 3.9+):**
```python
x: list[int] = [1, 2, 3]
```

---

## 🔹 2. `tuple` (кортеж)
Кортеж — **неизменяемая** упорядоченная коллекция.

```python
point = (10, 20)
```

**Особенности:**
- После создания изменить нельзя.
- Может использоваться как ключ в `dict`, если содержит только хэшируемые элементы.
- Используется там, где важна неизменяемость или производительность.

**Встроенный тип:** `tuple`  
**Типизация:**
```python
coords: tuple[int, int] = (10, 20)
```

---

## 🔹 3. `dict` (словарь)
Словарь — **изменяемая** коллекция пар **ключ: значение**.

```python
user = {"id": 1, "name": "Alice"}
```

**Особенности:**
- Ключи должны быть **уникальными и хэшируемыми**.
- Быстрый доступ к значениям по ключу.

**Встроенный тип:** `dict`  
**Типизация:**
```python
data: dict[str, int] = {"a": 1, "b": 2}
```

---

## 🔹 4. `set` (множество)
Множество — **неупорядоченная** коллекция **уникальных** элементов.

```python
items = {1, 2, 3}
```

**Особенности:**
- Не содержит дубликатов.
- Поддерживает операции множеств: пересечение, объединение и т.д.

**Встроенный тип:** `set`  
**Типизация:**
```python
unique_ids: set[int] = {1, 2, 3}
```

---

## ✅ Типизация в Python 3.12

С версии 3.9 (и в 3.12) можно использовать **встроенные обобщённые типы**:

```python
x: list[int]
y: dict[str, int]
z: tuple[int, str]
```

Также поддерживаются: `types.Unpack`, `TypedDict`, `NamedTuple`, `Union`, `Literal` и др.

---

## 🔍 Вложенные типы

```python
users: list[dict[str, str]] = [
    {"id": "1", "name": "Alice"},
    {"id": "2", "name": "Bob"}
]
```

---

## 🧠 Сводная таблица

| Тип     | Изменяемость | Упорядоченность | Уникальность | Пример               |
|---------|--------------|------------------|----------------|-----------------------|
| `list`  | ✅ да         | ✅ да            | ❌ нет         | `[1, 2, 3]`           |
| `tuple` | ❌ нет        | ✅ да            | ❌ нет         | `(1, 2)`              |
| `dict`  | ✅ да         | ✅ да (3.7+)     | ✅ по ключам   | `{"a": 1}`            |
| `set`   | ✅ да         | ❌ нет           | ✅ да          | `{1, 2, 3}`           |
