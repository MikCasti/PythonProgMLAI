import azure.functions as func
import logging
import os
import pyodbc

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

def get_connection():
    server=os.getenv("SQL_SERVER")
    database=os.getenv("SQL_DATABASE")
    username=os.getenv("SQL_USER")
    password=os.getenv("SQL_PASSWORD")
    driver= '{ODBC Driver 17 for SQL Server}'

    connection_string = (f'DRIVER={driver};'
                        f'SERVER={server};'
                        f'DATABASE={database};'
                        f'UID={username};'
                        f'PWD={password};'
    )
    return pyodbc.connect(connection_string)


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

@app.route(route="test")
def htttp_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT top 1 * from dbo.users")
        row = cursor.fetchone()
        conn.close()
    
    
        if row:
            return func.HttpResponse(f"Riga, {row[1]}", status_code=200.)
        else:
            return func.HttpResponse(
                "Nessun dato",
                status_code=400
            )
    except Exception as e:
        return func.HttpResponse(f"Error: {e}", status_code=500)