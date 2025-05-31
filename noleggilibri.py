import json
from datetime import datetime
import pyodbc 
import azure.functions as func
import logging
import azure.functions as func



app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.route(route="http_trigger")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
    

#INIZIALIZZAZIONE CON LA CONNESSIONE AL DATABASE
CONNECTION_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DATA-CASTILLO;"
    "DATABASE=Test_C001;"
    "Trusted_Connection=yes;")

def get_db_connection():
    try:
        return pyodbc.connect(CONNECTION_STRING)
    except Exception as e:
        logging.error(f"Errore connessione DB: {e}")
        return None
    


books_db = []
rentals_db = []


def main(req: func.HttpRequest) -> func.HttpResponse:
    method = req.method
    path = req.route_params.get('path')

    if method == 'GET' and path == 'books':
        return get_books()
    elif method == 'POST' and path == 'book':
        return add_book(req)
    elif method == 'POST' and path == 'rent':
        return rent_book(req)
    elif method == 'POST' and path == 'return':
        return return_book(req)
    elif method == 'GET' and path == 'unreturned-books':
        return get_unreturned_books()
    else:
        return func.HttpResponse("Not Found", status_code=404)

def get_books():
    return func.HttpResponse(json.dumps(books_db), mimetype="application/json")

def add_book(req):
    try:
        book = req.get_json()
        books_db.append(book)
        return func.HttpResponse("Book added successfully", status_code=201)
    except Exception as e:
        return func.HttpResponse(f"Error: {str(e)}", status_code=400)

def rent_book(req):
    try:
        rental = req.get_json()
        book_id = rental['book_id']
        user_id = rental['user_id']
        
        for book in books_db:
            if book['id'] == book_id:
                rentals_db.append({
                    "book_id": book_id,
                    "user_id": user_id,
                    "rental_date": datetime.now().isoformat()
                })
                return func.HttpResponse("Book rented successfully", status_code=201)
        return func.HttpResponse("Book not found", status_code=404)
    except Exception as e:
        return func.HttpResponse(f"Error: {str(e)}", status_code=400)

def return_book(req):
    try:
        return_info = req.get_json()
        book_id = return_info['book_id']
        user_id = return_info['user_id']
        
        for rental in rentals_db:
            if rental['book_id'] == book_id and rental['user_id'] == user_id:
                rentals_db.remove(rental)
                return func.HttpResponse("Book returned successfully", status_code=200)
        return func.HttpResponse("Rental not found", status_code=404)
    except Exception as e:
        return func.HttpResponse(f"Error: {str(e)}", status_code=400)

def get_unreturned_books():
    unreturned_books = []
    for rental in rentals_db:
        for book in books_db:
            if book['id'] == rental['book_id']:
                unreturned_books.append({
                    "book_id": rental['book_id'],
                    "title": book['title'],
                    "user_id": rental['user_id'],
                    "user_name": "User Name", 
                    "rental_date": rental['rental_date']
                })
    return func.HttpResponse(json.dumps(unreturned_books), mimetype="application/json")