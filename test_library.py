import pytest
from pydantic import ValidationError
from library import *

# Unit tests for the library system using pytest


# --- Object initialization tests ---

def test_initialization():
    # Test creation of a Book object
    book = Book("Shining" ,"Stephen King", "9781444720723", 2011)
    assert book.title == "Shining"
    assert book.author == "Stephen King"
    assert book.isbn == "9781444720723"
    assert book.publication_year == 2011

def test_ebook_initialization():
    # Test creation of an EBook object
    ebook = EBook("Dune", "Frank Herbert", "9780441172719", 1965, "EPUB")
    assert ebook.title == "Dune"
    assert ebook.author == "Frank Herbert"
    assert ebook.isbn == "9780441172719"
    assert ebook.publication_year == 1965
    assert ebook.file_format == "EPUB"
    assert ebook.book_type == "EBook"

def test_audiobook_initialization():
    # Test creation of a AudioBook object
    audiobook = AudioBook("Project Hail Mary", "Andy Weir", "9780593135211", 2021, 930)
    assert audiobook.title == "Project Hail Mary"
    assert audiobook.author == "Andy Weir"
    assert audiobook.isbn == "9780593135211"
    assert audiobook.publication_year == 2021
    assert audiobook.duration_min == 930
    assert audiobook.book_type == "AudioBook"


# --- Validation tests ---

def test_bookmodel_valid_data():
    # Test that valid data passes Pydantic model validation
    book_data = {
        "title": "The Catcher in the Rye",
        "author": "J.D. Salinger",
        "isbn": "9780316769488",
        "publication_year": 1951
    }
    book = BookModel(**book_data) # ** means dictionary unpacking
    assert book.title == "The Catcher in the Rye"

def test_bookmodel_invalid_isbn_length():
    # Test that invalid data (isbn) raises a ValidationError
    with pytest.raises(ValidationError):
        BookModel(title="Example", author="Author", isbn="short", publication_year=2000)

def test_bookmodel_invalid_publication_year():
    # Test that invalid data (publication year) raises a ValidationError
    with pytest.raises(ValidationError):
        BookModel(title="Example", author="Author", isbn="9780000000000", publication_year=1300)


# --- Library methods tests ---

# Fixture to create a sample library object
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
    # Test that show_books methods works correctly
    sample_library.show_books()
    captured = capsys.readouterr()
    assert "Great Book" in captured.out
    assert "Long Ebook" in captured.out
    assert "Fantastic AudioBook" in captured.out

def test_list_author_books(capsys, sample_library):
    # Test that list_author_books methods works correctly
    result = sample_library.list_author_books("Author A")
    titles = [book.title for book in result]
    assert "Great Book" in titles
    assert "Fantastic AudioBook" in titles
    assert "Long Ebook" not in titles 

def test_show_books_by_type(capsys, sample_library):
    # Test that show_books_by_type methods works correctly
    sample_library.show_books_by_type("ebook")
    captured = capsys.readouterr()
    assert "Long Ebook" in captured.out
    assert "Great Book" not in captured.out
    assert "Fantastic AudioBook" not in captured.out