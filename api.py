from fastapi import FastAPI, HTTPException
from typing import List
from library import Library, BookModel, BookRequest, BookResponse

# Create FastAPI application
app = FastAPI(
    title="Library API ",
    description="API for library management",
    version="1.0.0"
)

# Same file from step 1 and 2 
library = Library("library.json")

@app.get("/")
async def root():
    return {"message": "Welcome to the library API!"}

@app.get("/books", response_model=List[BookResponse])
async def get_books():
    #Lists all book from library
    books = []
    # Convert Book objects to BookResponse model
    for book in library._books:
        books.append(BookResponse(
            title=book.title,
            author=book.author,
            isbn=book.isbn,
            publication_year=book.publication_year,
            book_type=book.book_type
        ))
    return books

@app.post("/books", response_model=BookResponse)
async def add_book(book_request: BookRequest):
    # Add book by ISBN
    # Check if book is already in the library
    existing_book = library.find_book(book_request.isbn.replace('-', '').replace(' ', ''))
    if existing_book:
        raise HTTPException(
            status_code=400, 
            detail=f"Book with ISBN {book_request.isbn} already exists in the library."
        )
    
    # Fetch book information from API and add to library
    success = library.add_book_by_isbn(book_request.isbn)
    if not success:
        raise HTTPException(
            status_code=404, 
            detail="Book with ISBN not found or could not be retrieved."
        )
    
    # Find the book that is added and add to library
    added_book = library.find_book(book_request.isbn.replace('-', '').replace(' ', ''))
    return BookResponse(
        title=added_book.title,
        author=added_book.author,
        isbn=added_book.isbn,
        publication_year=added_book.publication_year,
        book_type=added_book.book_type
    )

@app.delete("/books/{isbn}")
async def delete_book(isbn: str):
    # Delete a book by ISBN

    clean_isbn = isbn.replace('-', '').replace(' ', '')

    # Check if the book exists
    book = library.find_book(clean_isbn)
    if not book:
        raise HTTPException(
            status_code=404, 
            detail=f"Book with ISBN {isbn} not found"
        )
    
    # Delete the book
    library.remove_book(clean_isbn)
    return {"message": f"Book with ISBN {isbn} deleted"}

@app.get("/books/{isbn}", response_model=BookResponse)
async def get_book(isbn: str):
    """ISBN ile belirli bir kitabı getir"""
    book = library.find_book(isbn.replace('-', '').replace(' ', ''))
    if not book:
        raise HTTPException(
            status_code=404, 
            detail=f"ISBN {isbn} ile kitap bulunamadı"
        )
    
    # Return book information
    return BookResponse(
        title=book.title,
        author=book.author,
        isbn=book.isbn,
        publication_year=book.publication_year,
        book_type=book.book_type
    )

