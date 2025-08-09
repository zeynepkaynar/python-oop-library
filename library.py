import json

# Represents a book in the library
class Book:
    def __init__(self, title: str, author: str, isbn: str, publication_year: int):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.publication_year = publication_year
        self.book_type = 'Book'

    def __str__(self):
        return f"'{self.title}' by {self.author} (ISBN: {self.isbn}, Publication year: {self.publication_year})"
    
    def to_dict(self):
        """Returns a dictionary representation of the book."""
        return self.__dict__

"""book = Book("1984", "George Orwell", "9780451524935", 1949)
print(book) """


class EBook(Book):
    def __init__(self, title: str, author: str, isbn: str, publication_year: int, file_format: str):
        super().__init__(title, author, isbn, publication_year)
        self.file_format = file_format
        self.book_type = 'EBook'

    def __str__(self):
        return f"{super().__str__()} [Format: {self.file_format}]"


class AudioBook(Book):
    def __init__(self, title: str, author: str, isbn: str, publication_year: int, duration_min: int):
        super().__init__(title, author, isbn, publication_year)
        self.duration_min = duration_min
        self.book_type = 'AudioBook'

    def __str__(self):
        return f"{super().__str__()} [Duration: {self.duration_min} mins]"
 

ebook = EBook("1984", "George Orwell", "978-0451524935", 1986, "EPUB")
audio_book = AudioBook("Becoming", "Michelle Obama", "978-1524763138", 1999, 780)

print(ebook)
print(audio_book)


class Library:
    def __init__(self, lib_name: str):
        self.lib_name = lib_name # JSON file name
        self._books = [] # _ means encapsulation 
        self.load_books()

    def add_book(self, book: Book):
        self._books.append(book)
        self.save_books()

    def remove_book(self, isbn: str):
        self._books = [book for book in self._books if book.isbn != isbn]
        self.save_books()
    
    def find_book(self, isbn: str):
        for book in self._books:
            if book.isbn == isbn:
                return book
        return None
    
    def show_books(self):
        for book in self._books:
            print(book)
        
    def load_books(self):
        try:
            with open(self.lib_name, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._books = []
                for item in data:
                    if item.get("book_type") == "EBook":
                        self._books.append(EBook(
                            item["title"], item["author"], item["isbn"],
                            item["publication_year"], item["file_format"]
                        ))
                    elif item.get("book_type") == "AudioBook":
                        self._books.append(AudioBook(
                            item["title"], item["author"], item["isbn"],
                            item["publication_year"], item["duration_min"]
                        ))
                    else:
                        self._books.append(Book(
                            item["title"], item["author"], item["isbn"],
                            item["publication_year"]
                        ))
        except FileNotFoundError:
            self._books = []


    def save_books(self):
        with open(self.lib_name, 'w', encoding='utf-8') as f:
            # Kitap nesnelerini dict haline çevirip kaydet
            json.dump([book.__dict__ for book in self._books], f, indent=4, ensure_ascii=False)


def main():
    library = Library("library.json")

    while True:
        print("\n1. Add a book\n2. Remove a book\n3. Show all books\n4. Search a book\n5. Exit")
        choice = input("Enter an option: ")

        if choice == "1":
            print("Book type:\n1. Book\n2. EBook\n3. AudioBook")
            type_choice = input("Choice: ")

            title = input("Title: ")
            author = input("Author: ")
            isbn = input("ISBN: ")
            pub_year = int(input("Publication year: "))

            if type_choice == "2":  # EBook
                file_format = input("File format (e.g., PDF, EPUB): ")
                book = EBook(title, author, isbn, pub_year, file_format)
            elif type_choice == "3":  # AudioBook
                duration_min = int(input("Duration (minutes): "))
                book = AudioBook(title, author, isbn, pub_year, duration_min)
            else:  # Normal Book
                book = Book(title, author, isbn, pub_year)

            library.add_book(book)
            print("Book added.")

        elif choice == "2":
            isbn = input("ISBN of the book being deleted: ")
            library.remove_book(isbn)
            print("Book deleted.")

        elif choice == "3":
            library.show_books()

        elif choice == "4":
            isbn = input("ISBN of the book being searched: ")
            book = library.find_book(isbn)
            if book:
                print(f"Found\n{book}")
            else:
                print("Not found.")

        elif choice == "5":
            break

        else:
            print("Invalid choice. Try again")


if __name__ == "__main__":
    main()
