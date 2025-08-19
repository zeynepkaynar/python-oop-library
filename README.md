# python-oop-library
## Global AI Hub Python 202 Bootcamp Project
### About the Project
This project is a 3-step library management system that presents the evolution from a simple console application to a web service </br>
1. A simple library management console application that is designed with OOP concepts. </br>
2. Automatic book information retrieval with Open Library API integration. </br>
3. With the help of FastAPI, turning the library application into a web service. </br> </br> 
The system supports multiple book types (physical books, eBooks, and audiobooks), which are created with OOP principles, provides persistent data storage in JSON format, includes error handling, and features test coverage with pytest. Users can add, remove, search, and categorize books both through an terminal interface and modern web API endpoints. </br>
### Setup
Installation: 
1. Clone the repository: `git clone https://github.com/[zeynepkaynar]/python-oop-library.git` </br>
`cd library-management-system`
2. Install dependencies: `pip install -r requirements.txt`
### Usage
1. Terminal Application (Step 1-2): Run the terminal application:  `python library.py` </br>
Menu options are provided, such as adding, deleting, searching a book etc. </br>
2. Web API Service (Step 3):  Start the API server: `uvicorn api:app --reload` </br>
API will be running at: http://127.0.0.1:8000 </br>
### API Documentation
Interactive Documentation </br>
Swagger UI: http://127.0.0.1:8000/docs </br>
ReDoc: http://127.0.0.1:8000/redoc </br> </br>
API Endpoints </br> 
- GET /: Welcome endpoint that confirms that FastAPI server is running </br>
- GET /books: Lists all the books in the library </br>
- POST /books: Automatically retrieves book information by ISBN and adds to library </br>
Example: Body structure for a POST request </br> </br>
POST /books </br>
Content-Type: application/json </br>
{ </br>
"isbn": "9781444720723" </br>
} </br> </br>
- GET /books/{isbn}: Returns a specific book by ISBN </br>
- DELETE /books/{isbn}: Removes the book with the given ISBN </br>
