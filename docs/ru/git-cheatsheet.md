
# 🧠 Git Шпаргалка

## 🧾 Базовые команды

| Задача                     | Команда                                           |
|----------------------------|---------------------------------------------------|
| Проверить состояние        | `git status`                                     |
| Посмотреть изменения      | `git diff`                                       |
| Добавить все файлы        | `git add .`                                      |
| Добавить конкретный файл  | `git add file.py`                                |
| Сделать коммит            | `git commit -m "Описание"`                       |
| Отправить на GitHub       | `git push`                                       |
| Склонировать репозиторий  | `git clone git@github.com:user/repo.git`        |
| Посмотреть историю        | `git log --oneline`                              |

---

## 🚀 Работа с удалённым репозиторием

```bash
git remote add origin git@github.com:username/repo.git
git push -u origin main  # Первый пуш
git push                 # Дальнейшие пуши
```

---

## 🔁 Сохраняем изменения

```bash
git add .
git commit -m "Что сделано"
git push
```

---

## 🧹 Очистка индекса (например, если `.gitignore` не сработал)

```bash
git rm -r --cached .
git add .
git commit -m "Fix .gitignore"
git push
```

---

## 🚫 Удаление последнего коммита (локально)

```bash
git reset --soft HEAD~1       # Удаляет коммит, сохраняет изменения
git reset --hard HEAD~1       # Удаляет коммит и изменения
```

---

## ⚙️ Работа с .gitignore

- Добавь файл `.gitignore`
- Пример:

```
__pycache__/
*.log
.env
*.pyc
dist/
node_modules/
```

- Проверить, почему файл игнорируется:

```bash
git check-ignore -v path/to/file
```

---

## 🔧 Удаление Git и повторная инициализация

```bash
rm -rf .git
git init
git remote add origin git@github.com:user/repo.git
git add .
git commit -m "Initial clean commit"
git push -f -u origin main
```

---

## 🌿 Работа с ветками

```bash
git branch                  # Показать список веток
git checkout -b new-branch # Создать и перейти в новую ветку
git checkout main          # Вернуться в main
git merge new-branch       # Слить ветку
git branch -d new-branch   # Удалить ветку
```

---

## 🧪 Отмена изменений

| Что отменить                         | Команда                                 |
|--------------------------------------|------------------------------------------|
| Все локальные изменения              | `git checkout -- .`                      |
| Только 1 файл                        | `git checkout -- file.py`               |
| Неиндексированные изменения          | `git restore file.py`                   |
| Отмена `git add` (до коммита)        | `git reset`                             |

---

## 🗂 Добавление пустых папок (Git их не видит)

```bash
touch path/to/folder/.gitkeep
```

И добавь:

```bash
git add .
```

---

## 🔄 Полный цикл работы

```bash
git pull
# Работа с кодом
git add .
git commit -m "..."
git push
```

---

## 🧩 Полезные команды

| Задача                         | Команда                                       |
|--------------------------------|-----------------------------------------------|
| Показать удалённые репозитории | `git remote -v`                               |
| Изменить URL `origin`          | `git remote set-url origin git@github.com...`|
| Сброс к последнему коммиту     | `git reset --hard HEAD`                       |
| Очистить все untracked файлы   | `git clean -fd`                               |
