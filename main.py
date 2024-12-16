import csv
import json
import tkinter as tk
from tkinter import messagebox

# Define the available genres
genres_list = [
    "Science Fiction",
    "Fantasy",
    "Mystery",
    "Romance",
    "Horror",
    "Historical Fiction",
    "Non-Fiction",
    "Adventure",
    "Children's Literature",
    "Classic Literature"
]


# Генератор для загрузки книг из JSON файла
def load_books(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            # Читаем весь файл и загружаем как список объектов
            data = json.load(f)
            for book in data:
                yield book  # Возвращаем каждую книгу по одной
    except FileNotFoundError:
        messagebox.showerror("Error", f"File '{filename}' not found.")
        return []
    except json.JSONDecodeError as e:
        messagebox.showerror("Error", f"Error decoding JSON from '{filename}': {str(e)}")
        return []


# Define the recommendation algorithm
def recommend_books(user_genres, user_authors, user_keywords, books, min_year):
    recommendations = []

    # Convert user inputs to lowercase for case-insensitive comparison
    user_genres = [genre.lower() for genre in user_genres]
    user_authors = [author.lower() for author in user_authors]
    user_keywords = [keyword.lower() for keyword in user_keywords]

    for book in books:
        score = 0

        # Check for genre matches (case-insensitive)
        if book['genre'].lower() in user_genres:
            score += 1

        # Check for author matches (partial match, case-insensitive)
        for author in user_authors:
            if any(author in book_author.lower() for book_author in book['author']):
                score += 1

        # Check for keyword matches in the description (case-insensitive)
        description = book.get('description', '').lower()
        keywords_matched = sum(1 for keyword in user_keywords if keyword in description)
        score += keywords_matched

        # Filter by minimum publication year
        if min_year and book.get('first_publish_year', 0) < min_year:
            continue  # Skip this book if it was published before min_year

        if score > 0:
            recommendations.append((book, score))

    return recommendations


# функция для получения рекомендаций
def get_recommendations():
    genres = [genre.strip() for genre in genres_entry.get().split(',')]
    authors = [author.strip() for author in authors_entry.get().split(',')]
    keywords = [keyword.strip() for keyword in keywords_entry.get().split(',')]

    # Получение минимального года публикации
    try:
        min_year = int(year_entry.get())
    except ValueError:
        min_year = None

    # Загрузка книг из JSON файла с использованием генератора
    books = load_books('books.json')

    # Получение рекомендаций на основе пользовательского ввода
    recommended_books = recommend_books(genres, authors, keywords, books, min_year)

    # Очистка предыдущих результатов
    listbox.delete(0, tk.END)

    # Отображение рекомендаций в Listbox
    if recommended_books:
        for book, score in recommended_books:
            formatted_res = f"Title: {book['title']}\n" \
                            f"Authors: {', '.join(book['author'])}\n" \
                            f"Published: {book.get('first_publish_year', 'N/A')}\n" \
                            f"Score: {score}\n" \
                            f"Description: {book.get('description', 'No description available.')}\n"
            listbox.insert(tk.END, formatted_res)
            listbox.insert(tk.END, "-" * 40)  # Добавление разделителя
    else:
        listbox.insert(tk.END, "No recommendations found.")


# Function to sort by score
def extract_book_info(item):
    """Вспомогательная функция для извлечения информации о книге из строки."""
    lines = item.split('\n')
    title = lines[0].replace("Title: ", "")
    authors = lines[1].replace("Authors: ", "").split(', ')
    score = int(lines[3].replace("Score: ", ""))
    pub_year = lines[2].replace("Published: ", "")
    description = lines[4].replace("Description: ", "")
    return title, authors, score, pub_year, description


def sort_by_score():
    items = listbox.get(0, tk.END)

    sorted_items = sorted(
        [extract_book_info(item) for item in items if "Title:" in item],
        key=lambda x: x[2],  # Sort by score
        reverse=True
    )

    update_listbox(sorted_items)


def sort_alphabetically():
    items = listbox.get(0, tk.END)

    sorted_items = sorted(
        [extract_book_info(item) for item in items if "Title:" in item],
        key=lambda x: x[0].lower()  # Sort by title (first element)
    )

    update_listbox(sorted_items)


def sort_by_publication_year():
    items = listbox.get(0, tk.END)

    sorted_items = sorted(
        [extract_book_info(item) for item in items if "Title:" in item],
        key=lambda x: (x[3] if x[3] != 'N/A' else float('inf'))  # Handle 'N/A' gracefully
    )

    update_listbox(sorted_items)


def update_listbox(sorted_items):
    """Обновляет Listbox с отсортированными элементами."""
    listbox.delete(0, tk.END)

    for title, authors, score, pub_year, description in sorted_items:
        formatted_res = f"Title: {title}\nAuthors: {', '.join(authors)}\nPublished: {pub_year}\nScore: {score}\nDescription: {description}\n"
        listbox.insert(tk.END, formatted_res)
        listbox.insert(tk.END, "-" * 40)


# Function to add selected book to "To Read" list
def add_to_read():
    selected_indices = listbox.curselection()

    if not selected_indices:
        messagebox.showwarning("Warning", "Please select a book to add to 'To Read'.")
        return

    for index in selected_indices:
        book_info = listbox.get(index)  # Get the formatted string

        # Check if the book_info is not a separator line
        if book_info.strip() == "-" * 40:  # Check for separator line
            continue

        if book_info not in to_read_listbox.get(0, tk.END):  # Avoid duplicates
            to_read_listbox.insert(tk.END, book_info)  # Add it to "To Read"


# Function to export "To Read" list to CSV file
def export_to_csv():
    with open('to_read_list.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        writer.writerow(["Title", "Authors", "Published Year", "Description"])  # Write header

        for i in range(to_read_listbox.size()):
            item_text = to_read_listbox.get(i).strip().split('\n')
            title = item_text[0].replace("Title: ", "")
            authors = item_text[1].replace("Authors: ", "")
            published_year = item_text[2].replace("Published: ", "")
            description = item_text[4].replace("Description: ", "")

            writer.writerow([title.strip(), authors.strip(), published_year.strip(), description.strip()])

    messagebox.showinfo("Export Successful", "To Read list exported successfully as 'to_read_list.csv'.")


# Function to export "To Read" list to JSON file
def export_to_json():
    to_read_books = []

    for i in range(to_read_listbox.size()):
        item_text = to_read_listbox.get(i).strip().split('\n')

        title = item_text[0].replace("Title: ", "")
        authors = item_text[1].replace("Authors: ", "").split(', ')

        published_year = item_text[2].replace("Published: ", "")
        description = item_text[4].replace("Description: ", "")

        to_read_books.append({
            'title': title,
            'authors': authors,
            'published_year': published_year,
            'description': description,
        })

    with open('to_read_list.json', 'w', encoding='utf-8') as json_file:
        json.dump(to_read_books, json_file, ensure_ascii=False, indent=4)

    messagebox.showinfo("Export Successful", "To Read list exported successfully as 'to_read_list.json'.")


# Function to show available genres
def show_genres():
    genre_list = "\n".join(genres_list)
    messagebox.showinfo("Available Genres", genre_list)


# Main application window setup
root = tk.Tk()
root.title("Book Recommendation System")
root.geometry("530x650")

# Labels and Entry fields for user input
tk.Label(root, text="Favorite Genres (comma-separated):").grid(row=0, column=0)
genres_entry = tk.Entry(root, width=50)
genres_entry.grid(row=0, column=1)

tk.Label(root, text="Favorite Authors (comma-separated):").grid(row=1, column=0)
authors_entry = tk.Entry(root, width=50)
authors_entry.grid(row=1, column=1)

tk.Label(root, text="Preferred Keywords (comma-separated):").grid(row=2, column=0)
keywords_entry = tk.Entry(root, width=50)
keywords_entry.grid(row=2, column=1)

tk.Label(root, text="Minimum Publication Year:").grid(row=3, column=0)
year_entry = tk.Entry(root, width=50)
year_entry.grid(row=3, column=1)

# Button to get recommendations
recommend_button = tk.Button(root, text="Get Recommendations", command=get_recommendations)
recommend_button.grid(row=4, columnspan=2)

# Button to show available genres
show_genres_button = tk.Button(root, text="Show Available Genres", command=show_genres)
show_genres_button.grid(row=5, columnspan=2)

# Create Listbox and Scrollbar for displaying recommendations
listbox_frame = tk.Frame(root)
listbox_frame.grid(row=6, columnspan=2)

listbox = tk.Listbox(listbox_frame, width=70, height=10)
listbox.pack(side=tk.LEFT)

scrollbar = tk.Scrollbar(listbox_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=listbox.yview)

# Create Listbox for "To Read" list
to_read_frame = tk.Frame(root)
to_read_frame.grid(row=7, columnspan=2)

to_read_listbox = tk.Listbox(to_read_frame, width=70, height=10)
to_read_listbox.pack(side=tk.LEFT)

to_read_scrollbar = tk.Scrollbar(to_read_frame)
to_read_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

to_read_listbox.config(yscrollcommand=to_read_scrollbar.set)
to_read_scrollbar.config(command=to_read_listbox.yview)

# Button to add selected book to "To Read" list
add_to_read_button = tk.Button(root, text="Add to 'To Read'", command=lambda: add_to_read())
add_to_read_button.grid(row=8, columnspan=2)

# Buttons for sorting options
sort_score_button = tk.Button(root, text="Sort by Score", command=sort_by_score)
sort_score_button.grid(row=9, columnspan=2)

sort_alpha_button = tk.Button(root, text="Sort Alphabetically", command=sort_alphabetically)
sort_alpha_button.grid(row=10, columnspan=2)

sort_year_button = tk.Button(root, text="Sort by Publication Year", command=sort_by_publication_year)
sort_year_button.grid(row=11, columnspan=2)

# Button to export To Read list as CSV and JSON files
export_csv_button = tk.Button(root, text="Export To Read List as CSV", command=export_to_csv)
export_csv_button.grid(row=12, columnspan=2)

export_json_button = tk.Button(root, text="Export To Read List as JSON", command=export_to_json)
export_json_button.grid(row=13, columnspan=2)

# Run the application loop
root.mainloop()