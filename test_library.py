import pytest
from pydantic import ValidationError
from library import *
import json

# -------------------
# Object initialization tests
# -------------------

def test_initialization():
    book = Book("Shining", "Stephen King", "9781444720723", 2011)
    assert book.title == "Shining"
    assert book.author == "Stephen King"
    assert book.isbn == "9781444720723"
    assert book.publication_year == 2011

def test_ebook_initialization():
    ebook = EBook("Dune", "Frank Herbert", "9780441172719", 1965, "EPUB")
    assert ebook.title == "Dune"
    assert ebook.author == "Frank Herbert"
    assert ebook.isbn == "9780441172719"
    assert ebook.publication_year == 1965
    assert ebook.file_format == "EPUB"
    assert ebook.book_type == "EBook"

def test_audiobook_initialization():
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
    book_data = {
        "title": "The Catcher in the Rye",
        "author": "J.D. Salinger",
        "isbn": "9780316769488",
        "publication_year": 1951
    }
    book = BookModel(**book_data)
    assert book.title == "The Catcher in the Rye"

def test_bookmodel_invalid_isbn_length():
    with pytest.raises(ValidationError):
        BookModel(title="Example", author="Author", isbn="short", publication_year=2000)

def test_bookmodel_invalid_publication_year():
    with pytest.raises(ValidationError):
        BookModel(title="Example", author="Author", isbn="9780000000000", publication_year=1300)

# -------------------
# Library method tests
# -------------------

@pytest.fixture
def sample_library():
    lib = Library(lib_name="SampleLibrary")
    lib._books = [
        Book(title="Great Book", author="Author A", isbn="1111111111111", publication_year=2020),
        EBook(title="Long Ebook", author="Author B", isbn="2222222222222", publication_year=2021, file_format="pdf"),
        AudioBook(title="Fantastic AudioBook", author="Author A", isbn="3333333333333", publication_year=2019, duration_min=90),
    ]
    return lib

def test_show_books(capsys, sample_library):
    sample_library.show_books()
    captured = capsys.readouterr()
    assert "Great Book" in captured.out
    assert "Long Ebook" in captured.out
    assert "Fantastic AudioBook" in captured.out

def test_list_author_books(sample_library):
    result = sample_library.list_author_books("Author A")
    titles = [book.title for book in result]
    assert "Great Book" in titles
    assert "Fantastic AudioBook" in titles
    assert "Long Ebook" not in titles

def test_show_books_by_type(capsys, sample_library):
    sample_library.show_books_by_type("ebook")
    captured = capsys.readouterr()
    assert "Long Ebook" in captured.out
    assert "Great Book" not in captured.out
    assert "Fantastic AudioBook" not in captured.out

# -------------------
# API integration tests
# -------------------

def test_fetch_book_from_api(monkeypatch):

    # Mock function does not make real API calls
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
    # Mock function simulates book not found
    def mock_get_book(isbn):
        return None
    lib = Library(lib_name="test_library.json")
    monkeypatch.setattr(lib, "fetch_book_from_api", mock_get_book)
    # Test API call for non-existent book
    result = lib.fetch_book_from_api("0000000000")
    assert result is None


def test_add_book_by_isbn(monkeypatch, tmp_path):
    # Create temporary test file
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
    test_file = tmp_path / "library.json"
    lib = Library(lib_name=str(test_file))
    result = lib.add_book_by_isbn("invalid_isbn")
    assert result is False


def test_add_book_by_isbn_already_exists(monkeypatch, tmp_path):
    test_file = tmp_path / "library.json"
    lib = Library(lib_name=str(test_file))

    # Add a book to library 
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


def test_add_ebook_by_isbn(monkeypatch, tmp_path):
    test_file = tmp_path / "library.json"
    lib = Library(lib_name=str(test_file))

    def mock_get_book(isbn):
        return {
            "title": "EBook Title",
            "author": "EBook Author",
            "isbn": isbn,
            "publication_year": 2021
        }
    monkeypatch.setattr(lib, "fetch_book_from_api", mock_get_book)

    added = lib.add_book_by_isbn("1234567890", book_type="ebook", file_format="PDF")
    assert added is True
    assert isinstance(lib._books[0], EBook)
    assert lib._books[0].file_format == "PDF"


def test_add_audiobook_by_isbn(monkeypatch, tmp_path):
    test_file = tmp_path / "library.json"
    lib = Library(lib_name=str(test_file))

    def mock_get_book(isbn):
        return {
            "title": "Audio Title",
            "author": "Audio Author",
            "isbn": isbn,
            "publication_year": 2020
        }
    monkeypatch.setattr(lib, "fetch_book_from_api", mock_get_book)

    added = lib.add_book_by_isbn("1234567890", book_type="audiobook", duration_min=120)
    assert added is True
    assert isinstance(lib._books[0], AudioBook)
    assert lib._books[0].duration_min == 120

