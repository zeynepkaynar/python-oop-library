import pytest
from pydantic import ValidationError
from library import *
from fastapi.testclient import TestClient
import api

# -------------------
# Object initialization tests
# -------------------

def test_initialization():
    # Test that Book object is initialized with its correct attributes
    book = Book("Shining", "Stephen King", "9781444720723", 2011)
    assert book.title == "Shining"
    assert book.author == "Stephen King"
    assert book.isbn == "9781444720723"
    assert book.publication_year == 2011

def test_ebook_initialization():
    # Test that EBook object is initialized with its correct attributes
    ebook = EBook("Dune", "Frank Herbert", "9780441172719", 1965, "EPUB")
    assert ebook.title == "Dune"
    assert ebook.author == "Frank Herbert"
    assert ebook.isbn == "9780441172719"
    assert ebook.publication_year == 1965
    assert ebook.file_format == "EPUB"
    assert ebook.book_type == "EBook"

def test_audiobook_initialization():
    # Test that AudioBook object is initialized with its correct attributes
    audiobook = AudioBook("Project Hail Mary", "Andy Weir", "9780593135211", 2021, 930)
    assert audiobook.title == "Project Hail Mary"
    assert audiobook.author == "Andy Weir"
    assert audiobook.isbn == "9780593135211"
    assert audiobook.publication_year == 2021
    assert audiobook.duration_min == 930
    assert audiobook.book_type == "AudioBook"

# -------------------
# Pydantic validation tests
# -------------------

def test_bookmodel_valid_data():
    # Test that BookModel accepts valid book data
    book_data = {
        "title": "The Catcher in the Rye",
        "author": "J.D. Salinger",
        "isbn": "9780316769488",
        "publication_year": 1951
    }
    book = BookModel(**book_data)
    assert book.title == "The Catcher in the Rye"

def test_bookmodel_invalid_isbn_length():
    # Test that BookModel raises ValidationError when ISBN is invalid
    with pytest.raises(ValidationError):
        BookModel(title="Example", author="Author", isbn="short", publication_year=2000)

def test_bookmodel_invalid_publication_year():
    # Test that BookModel raises ValidationError when publication year is invalid
    with pytest.raises(ValidationError):
        BookModel(title="Example", author="Author", isbn="9780000000000", publication_year=1300)

# -------------------
# Library method tests
# -------------------

 #A pytest fixture is a reusable function that gives tests prepared data or objects.
@pytest.fixture
def sample_library():
    # Create sample library and add sample books
    lib = Library(lib_name="SampleLibrary")
    lib._books = [
        Book(title="Great Book", author="Author A", isbn="1111111111111", publication_year=2020),
        EBook(title="Long Ebook", author="Author B", isbn="2222222222222", publication_year=2021, file_format="pdf"),
        AudioBook(title="Fantastic AudioBook", author="Author A", isbn="3333333333333", publication_year=2019, duration_min=90),
    ]
    return lib

def test_show_books(capsys, sample_library):
    # Test that show_books() displays all books in the library correctly.
    sample_library.show_books()
    captured = capsys.readouterr() # Capture stdout output
    assert "Great Book" in captured.out
    assert "Long Ebook" in captured.out
    assert "Fantastic AudioBook" in captured.out

def test_list_author_books(sample_library):
    # Test that list_author_books() returns the books written by the given author
    result = sample_library.list_author_books("Author A")
    titles = [book.title for book in result]
    assert "Great Book" in titles
    assert "Fantastic AudioBook" in titles
    assert "Long Ebook" not in titles

def test_show_books_by_type(capsys, sample_library):
    # Test that show_books_by_type() shows books from specified type
    sample_library.show_books_by_type("ebook")
    captured = capsys.readouterr()
    assert "Long Ebook" in captured.out
    assert "Great Book" not in captured.out
    assert "Fantastic AudioBook" not in captured.out

# -------------------
# API integration tests
# -------------------

def test_fetch_book_from_api(monkeypatch):
    # Test that the mocked fetch_book_from_api() returns expected data structure
    # Mock function does not make real API calls, it simulates API response
    def mock_get_book(isbn):
        return {
            "title": "Mock Title",
            "author": "Mock Author",
            "isbn": isbn,
            "publication_year": 2024
        }
    lib = Library(lib_name="test_library.json")

    # Replace fetch_book_from_api method with mock function
    monkeypatch.setattr(lib, "fetch_book_from_api", mock_get_book)

    result = lib.fetch_book_from_api("1234567890")
    assert result["title"] == "Mock Title"
    assert result["author"] == "Mock Author"


def test_fetch_book_from_api_not_found(monkeypatch):
    # Test that fetch_book_from_api() returns None when book is not found in API
    # Mock function simulates book not found
    def mock_get_book(isbn):
        return None
    lib = Library(lib_name="test_library.json")
    monkeypatch.setattr(lib, "fetch_book_from_api", mock_get_book)
    # Test API call for non-existent book
    result = lib.fetch_book_from_api("0000000000")
    assert result is None


def test_add_book_by_isbn(monkeypatch, tmp_path):
    # Test that add_book_by_isbn() adds a book when API returns valid data
    # Create temporary test file to avoid affecting real library
    test_file = tmp_path / "library.json"
    lib = Library(lib_name=str(test_file))
    # Mock function that simulates successful API response
    def mock_get_book(isbn):
        return {
            "title": "Mock Title",
            "author": "Mock Author",
            "isbn": isbn,
            "publication_year": 2024
        }
    monkeypatch.setattr(lib, "fetch_book_from_api", mock_get_book)
    added = lib.add_book_by_isbn("1234567890")
    assert added is True
    assert len(lib._books) == 1
    assert lib._books[0].title == "Mock Title"


def test_add_book_by_isbn_invalid_isbn(tmp_path):
    # Test that add_book_by_isbn() returns False when ISBN is invalid
    test_file = tmp_path / "library.json"
    lib = Library(lib_name=str(test_file))
    result = lib.add_book_by_isbn("invalid_isbn")
    assert result is False


def test_add_book_by_isbn_already_exists(monkeypatch, tmp_path):
    # Test that add_book_by_isbn() returns False when the given book already exists
    test_file = tmp_path / "library.json"
    lib = Library(lib_name=str(test_file))

    # Add a book to library first
    lib._books.append(Book("Existing", "Author", "1234567890", 2023))

    def mock_get_book(isbn):
        return {
            "title": "Mock Title",
            "author": "Mock Author",
            "isbn": isbn,
            "publication_year": 2024
        }
    monkeypatch.setattr(lib, "fetch_book_from_api", mock_get_book)

    # Test adding a book with the same ISBN
    result = lib.add_book_by_isbn("1234567890")
    assert result is False

# -------------------
# API endpoint tests
# -------------------

@pytest.fixture
def test_client(tmp_path, monkeypatch):
    # Create temporary test client and library
    # Temporary JSON file
    temp_file = tmp_path / "test_library.json"
    test_library = Library(lib_name=str(temp_file))

    # Replace the real library with the test library
    monkeypatch.setattr(api, "library", test_library)

    # FastAPI TestClient bound to the app
    client = TestClient(api.app)
    return client, test_library


def test_root_endpoint(test_client):
    # Test root endpoint returns welcome message
    client, _ = test_client
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the library API!"}


def test_get_books_empty(test_client):
    # Test get(/books) returns empty list when no books exist
    client, _ = test_client
    response = client.get("/books")
    assert response.status_code == 200
    assert response.json() == []


def test_add_book(test_client, monkeypatch):
    # Test post.(/books) successfully adds a new book
    client, test_library = test_client

    # Mock function does not make real API calls
    def mock_fetch(isbn):
        return {
            "title": "Mock Title",
            "author": "Mock Author",
            "isbn": isbn,
            "publication_year": 2024,
        }
    
    # Replace fetch_book_from_api method with mock function
    monkeypatch.setattr(test_library, "fetch_book_from_api", mock_fetch)

    response = client.post("/books", json={"isbn": "1234567890"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Mock Title"
    assert data["author"] == "Mock Author"


def test_get_book_found(test_client):
    # Test get.(/books/{isbn}) returns the correct book
    client, test_library = test_client
    book = Book("Test Title", "Test Author", "9876543210", 2022)
    test_library._books.append(book)

    response = client.get(f"/books/{book.isbn}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Title"
    assert data["isbn"] == "9876543210"


def test_get_book_not_found(test_client):
    # Test get.(/books/{isbn}) returns 404 if book does not exist"
    client, _ = test_client
    response = client.get("/books/0000000000")
    assert response.status_code == 404


def test_delete_book(test_client):
    # Test delete.(/books/{isbn}) deletes a book successfully
    client, test_library = test_client
    book = Book("Delete Me", "Author", "5555555555", 2015)
    test_library._books.append(book)

    response = client.delete(f"/books/{book.isbn}")
    assert response.status_code == 200
    assert "deleted" in response.json()["message"]


def test_delete_book_not_found(test_client):
    # Test delete.(/books/{isbn}) returns 404 if book does not exist
    client, _ = test_client
    response = client.delete("/books/9999999999")
    assert response.status_code == 404