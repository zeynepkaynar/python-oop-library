from fastapi import FastAPI, HTTPException
from typing import List
from library import Library, BookRequest, BookResponse, normalize_isbn

# Create FastAPI application
app = FastAPI(
    title="Library API",
    description="API for library management",
    version="1.0.0"
)

# Same file from step 1 and 2 
library = Library("library.json")

@app.get("/")
# Root endpoind prints a welcome message to confirm API is running
async def root():
    return {"message": "Welcome to the library API!"}

@app.get("/books", response_model=List[BookResponse])
async def get_books():
    # Lists all book from library
    books = []
    # Convert Book objects in library to BookResponse model for API response
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

    clean_isbn = normalize_isbn(book_request.isbn)
    if len(clean_isbn) not in (10, 13):
        raise HTTPException(
            status_code=422,
            detail="ISBN must be either 10 or 13 characters long."
        )
    
    # Check if book is already in the library
    existing_book = library.find_book(clean_isbn)
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
    
    # Find the book that is added and return it
    added_book = library.find_book(clean_isbn)
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

    clean_isbn = normalize_isbn(isbn)

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
    # Get a specific book by ISBN
    clean_isbn =  normalize_isbn(isbn)

    # Find the book
    book = library.find_book(clean_isbn)
    if not book:
        raise HTTPException(
            status_code=404, 
            detail=f"Book with ISBN {clean_isbn} not found"
        )
    
    # Return book information
    return BookResponse(
        title=book.title,
        author=book.author,
        isbn=book.isbn,
        publication_year=book.publication_year,
        book_type=book.book_type
    )

