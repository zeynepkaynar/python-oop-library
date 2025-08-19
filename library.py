from enum import IntEnum
from pydantic import BaseModel, Field
import httpx
import json

# Represents a book in the library
class Book:
    def __init__(self, title: str, author: str, isbn: str, publication_year: int):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.publication_year = publication_year
        self.book_type = 'Book'

    # Overriding __str__ method
    def __str__(self):
        return f"'{self.title}' by {self.author} (ISBN: {self.isbn}, Publication year: {self.publication_year})"
    

# Represents an ebook in the library, subclass of Book
class EBook(Book):
    def __init__(self, title: str, author: str, isbn: str, publication_year: int, file_format: str):
        super().__init__(title, author, isbn, publication_year)
        self.file_format = file_format
        self.book_type = 'EBook'

    # Overriding __str__ method of the superclass
    def __str__(self):
        return f"{super().__str__()} [Format: {self.file_format}]"


# Represents an audio book in the library, subclass of Book
class AudioBook(Book):
    def __init__(self, title: str, author: str, isbn: str, publication_year: int, duration_min: int):
        super().__init__(title, author, isbn, publication_year)
        self.duration_min = duration_min
        self.book_type = 'AudioBook'
    
    # Overriding __str__ method of the superclass
    def __str__(self):
        return f"{super().__str__()} [Duration: {self.duration_min} mins]"

# Request and Response Models 
class BookRequest(BaseModel):
    isbn: str = Field(..., description="ISBN number (must be 10 or 13 characters):",
                min_length=10, max_length=13)

class BookResponse(BaseModel):
    title: str
    author: str
    isbn: str
    publication_year: int
    book_type: str = "Book"
    
# Pydantic Model
class BookModel(BaseModel):
    title: str
    author: str 
    isbn: str = Field(..., min_length=10, max_length=13)
    publication_year: int = Field(..., gt=1400)
    book_type: str = Field(default="Book")

# HTTP Status Codes
class HTTPStatusCodes(IntEnum):
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    UNPROCESSABLE_ENTITY = 422

def normalize_isbn(isbn: str) -> str:
    # Helper function to clean ISBN from spaces and hyphens
    return isbn.replace("-", "").replace(" ", "")

# Represents a library class
class Library:
    def __init__(self, lib_name: str):
        self.lib_name = lib_name # JSON file name
        self._books = [] # _ means encapsulation 
        self.load_books() # Books are loaded when the library is initialized


    def fetch_book_from_api(self, isbn: str):
        # Fetch book information from Open Library search.json API using ISBN

        OPEN_LIBRARY_URL = "https://openlibrary.org/search.json"
        try:
            clean_isbn = normalize_isbn(isbn)
            response = httpx.get(OPEN_LIBRARY_URL, params={"isbn": clean_isbn}, timeout=10.0)
            response.raise_for_status()
            data = response.json()

            # If no book data is returned, return None
            if not data.get("docs"):
                return None
            
            book_info = data["docs"][0]
            # Get related information or use default values
            title = book_info.get("title", "Unknown Title")
            author_names = book_info.get("author_name", [])
            author = ", ".join(author_names) if author_names else "Unknown Author" 
            publication_year = book_info.get("first_publish_year", None)

            # Return the book information as a dictionary
            return {
                "title": title,
                "author": author,
                "isbn": clean_isbn,
                "publication_year": publication_year
            }

        # Error handling
        except httpx.RequestError as e:
            print(f"Network error: {e}")
            return None
        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    def add_book_by_isbn(self, isbn: str, book_type: str = "Book", **kwargs):
        # **kwargs: Additional parameters depending on book type (e.g: audiobook, ebook)
        clean_isbn = normalize_isbn(isbn)
        if len(clean_isbn) not in (10, 13):
            print(f"Invalid ISBN: {isbn}. ISBN must be 10 or 13 characters.")
            return False
        
        # Check if book is already in the library
        if self.find_book(clean_isbn):
            print(f"Book with ISBN {clean_isbn} already exists in the library.")
            return False

        book_data = self.fetch_book_from_api(clean_isbn)   
        # If the book is not found or API request fails, print the message and return False
        if book_data is None:
            print(f"Book with ISBN {clean_isbn} not found or could not be retrieved.")
            return False
        
        # Create book object 
        try:
            if book_type.lower() == "ebook":
                # eBook-specific attribute: file format
                file_format = kwargs.get('file_format')
                book = EBook(
                    book_data['title'], 
                    book_data['author'], 
                    book_data['isbn'], 
                    book_data['publication_year'], 
                    file_format
                )
            elif book_type.lower() == "audiobook":
                # audiobook-specific attribute: duration in minutes
                duration_min = kwargs.get('duration_min')
                book = AudioBook(
                    book_data['title'], 
                    book_data['author'], 
                    book_data['isbn'], 
                    book_data['publication_year'], 
                    duration_min
                )
            else:
                book = Book(
                    book_data['title'], 
                    book_data['author'], 
                    book_data['isbn'], 
                    book_data['publication_year']
                )
            
            self._books.append(book)
            self.save_books()
            print(f"Book added successfully: {book}")
            return True
            
        except Exception as e:
            print(f"Error creating book object: {e}")
            return False

    def add_book(self, book: Book):
        # Old method from step 1
        self._books.append(book)
        self.save_books()

    def remove_book(self, isbn: str):
        # Remove a book by ISBN
        clean_isbn = normalize_isbn(isbn)
        self._books = [book for book in self._books if normalize_isbn(book.isbn) != clean_isbn]
        self.save_books()
    
    def find_book(self, isbn: str):
        # Find a book by ISBN
        clean_isbn = normalize_isbn(isbn)
        for book in self._books:
            if normalize_isbn(book.isbn) == clean_isbn:
                return book
        # If no match is found, return None
        return None
    
    def show_books(self):
        # List books if exist
        if not self._books:
            print("No books in the library.")
            return
        for book in self._books:
            print(book)

    def list_author_books(self, author: str):
        # List books by author name
        matches = [book for book in self._books if book.author.lower() == author.lower()]
        return matches

    def show_books_by_type(self, book_type: str):
        # List books of a kind
        found_books = False
        for book in self._books:
            if book.book_type.lower() == book_type.lower():
                print(book)
                found_books = True
        if not found_books:
            print(f"No books of type '{book_type}' found in the library.")
        
    def load_books(self):
        try:
            # Open the JSON file
            with open(self.lib_name, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._books = []
                for item in data:
                    # Check book type and create the according object
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
                            item["title"], item["author"], item["isbn"], item["publication_year"]
                        ))

        except FileNotFoundError:
            # If file does not exist, initialize empty list
            self._books = [] # 

    def save_books(self):
        # Save all books to the JSON file
        with open(self.lib_name, 'w', encoding='utf-8') as f:
            # Transform book objects to dictionaries
            json.dump([book.__dict__ for book in self._books], f, indent=4, ensure_ascii=False)


# Main menu 
def main():
    # Create Library object
    library = Library("library.json")

    while True:
        # Menu options
        print("\n1. Add a book\n2. Remove a book\n3. Show all books\n" \
        "4. Search a book\n5. Show an author's books\n6. List books by type\n7. Exit")
        choice = input("Enter an option: ")

        if choice == "1":
            print("Book type:\n1. Book\n2. EBook\n3. AudioBook")
            type_choice = input("Choice: ")

            isbn = input("Enter ISBN: ")
            # Add books according to their types 
            if type_choice == "2":  # EBook
                file_format = input("File format (e.g., PDF, EPUB): ")
                library.add_book_by_isbn(isbn, "ebook", file_format=file_format)
            elif type_choice == "3":  # AudioBook
                try:
                    duration_min = int(input("Duration (minutes): "))
                    library.add_book_by_isbn(isbn, "audiobook", duration_min=duration_min)
                except ValueError:
                    print("Invalid duration.")
                    library.add_book_by_isbn(isbn, "audiobook", duration_min=0)
            else:  # Normal Book
                library.add_book_by_isbn(isbn)

        elif choice == "2":
            isbn = input("ISBN of the book being deleted: ")
            book = library.find_book(isbn)
            if book:
                library.remove_book(isbn)
                print("Book deleted.")
            else:
                print("Book not found.")

        elif choice == "3":
            library.show_books()

        elif choice == "4":
            isbn = input("ISBN of the book being searched: ")
            book = library.find_book(isbn)
            if book:
                print(f"Found:\n{book}")
            else:
                print("Book not found.")

        elif choice == "5":
            author = input("Enter author name: ")
            books = library.list_author_books(author)
            if books:
                for book in books:
                    print(book)
            else:
                print(f"No books found by {author}.")

        elif choice == "6":
            book_type = input("Enter a book type (book, ebook, audiobook): ")
            library.show_books_by_type(book_type)

        elif choice == "7":
            break

        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()