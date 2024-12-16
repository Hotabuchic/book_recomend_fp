import json
import random

# Список возможных жанров и авторов
genres = ["Mystery", "Fantasy", "Science Fiction", "Romance", "Horror", "Historical Fiction"]
authors = ["Author A", "Author B", "Author C", "Author D", "Author E"]

# Функция для генерации книги
def generate_book(index):
    return {
        "title": f"Book Title {index}",
        "genre": random.choice(genres),
        "author": [random.choice(authors)],
        "first_publish_year": random.randint(1800, 2023),
        "description": f"This is a description for Book Title {index}."
    }

# Генерация 1000 книг
books = [generate_book(i) for i in range(1, 1001)]

# Сохранение в JSON файл
with open('books.json', 'w') as json_file:
    json.dump(books, json_file, indent=4)
