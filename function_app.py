import azure.functions as func
import logging
import pyodbc
import json 


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
    
#POST/ cantanti 
#Descrizione: Aggiunge un cantante al database
@app.route(route="add_cantanti", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
def add_cantanti(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    try:
        req_body = req.get_json()
        nome = req_body.get('nome')
        if not nome:
            return func.HttpResponse("Nome del cantante mancante", status_code=400)
        
        conn = get_db_connection()
        if conn is None:
            return func.HttpResponse("Errore connessione al DB", status_code=500)
        
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Cantanti (nome) VALUES (?)", nome)
        conn.commit()
        cursor.close()
        conn.close()
        return func.HttpResponse('{"message": "Cantante aggiunto con successo"}', status_code=200, mimetype="application/json")
    except Exception as e:
        logging.error(f"Errore aggiunta cantante: {e}")
        return func.HttpResponse("Errore aggiunta cantante", status_code=500)

#POST/ utenti
#Descrizione: Aggiunge un utente al database
@app.route(route="add_utenti", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
def add_utenti(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    try:
        req_body = req.get_json()
        nome_utente = req_body.get('nome_utente')
        if not nome_utente:
            return func.HttpResponse("Nome utente mancante", status_code=400)
        
        conn = get_db_connection()
        if conn is None:
            return func.HttpResponse("Errore connessione al DB", status_code=500)
        
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Utenti (nome_utente) VALUES (?)", nome_utente)
        conn.commit()
        cursor.close()
        conn.close()
        return func.HttpResponse('{"message": "Utente aggiunto con successo"}', status_code=200, mimetype="application/json")
    except Exception as e:
        logging.error(f"Errore aggiunta utente: {e}")
        return func.HttpResponse("Errore aggiunta utente", status_code=500)

#POST/ punteggi
#Decrizione: Assegna punti(positivi o negativi) ad un cantante
@app.route(route="post_punteggi", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
def post_punteggi(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    try:
        req_body = req.get_json()
        cantante_id = req_body.get('cantante_id')
        punti = req_body.get('punti')
        descrizione = req_body.get('descrizione')

        if not cantante_id or punti is None or not descrizione:
            return func.HttpResponse("Dati mancanti", status_code=400)

        conn = get_db_connection()
        if conn is None:
            return func.HttpResponse("Errore connessione al DB", status_code=500)

        cursor = conn.cursor()
        cursor.execute("INSERT INTO Punteggi (cantante_id, punti, descrizione) VALUES (?, ?, ?)", cantante_id, punti, descrizione)
        conn.commit()
        cursor.close()
        conn.close()
        return func.HttpResponse('{"message": "Punteggio aggiornato"}', status_code=200, mimetype="application/json")
    except Exception as e:
        logging.error(f"Errore aggiunta punteggio: {e}")
        return func.HttpResponse("Errore aggiunta punteggio", status_code=500)
    

#POST/ squadra
#Descrizione: aggiunge un solo cantante alla volta alla squadra di un utente(max 5 cantanti per squadra)
@app.route(route="post_squadra", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
def post_squadra(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    try:
        req_body = req.get_json()
        utente_id = req_body.get('utente_id')
        cantante_id = req_body.get('cantante_id')

        if not utente_id or not cantante_id:
            return func.HttpResponse("Dati mancanti", status_code=400)

        conn = get_db_connection()
        if conn is None:
            return func.HttpResponse("Errore connessione al DB", status_code=500)
        
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Squadra WHERE utente_id = ?", utente_id)
        count = cursor.fetchone()[0]
        if count >= 5:
            return func.HttpResponse('{"error": "La squadra ha già 5 cantanti"}', status_code=400, mimetype="application/json")
        
        cursor.execute("INSERT INTO Squadra (utente_id, cantante_id) VALUES (?, ?)", utente_id, cantante_id)
        conn.commit()
        cursor.close()
        conn.close()
        return func.HttpResponse('{"message": "Cantante aggiunto alla squadra"}', status_code=200, mimetype="application/json")
    except Exception as e:
        logging.error(f"Errore aggiunta cantante alla squadra: {e}")
        return func.HttpResponse("Errore aggiunta cantante alla squadra", status_code=500)

#GET/punti/squadra/{utente_id}
#Descrizione: Recupera il punteggio totale della squadra di un utente
@app.route(route="get_punti_squadra/{utente_id}", methods=["GET"], auth_level=func.AuthLevel.FUNCTION)
def get_punti_squadra(req: func.HttpRequest) -> func.HttpResponse:
    utente_id = int(req.route_params.get('utente_id'))
    logging.info('Python HTTP trigger function processed a request.')
    try:
        conn = get_db_connection()
        if conn is None:
            return func.HttpResponse("Errore connessione al DB", status_code=500)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT SUM(p.punti) as punti_totali
            FROM Squadra s
            JOIN Punteggi p ON s.cantante_id = p.cantante_id
            WHERE s.utente_id = ?
        """, utente_id)
        punti_totali = cursor.fetchone()[0]
        if punti_totali is None:
            punti_totali = 0
        cursor.close()
        conn.close()
        
        return func.HttpResponse(f'{{"utente_id": {utente_id}, "punti_totali": {punti_totali}}}', status_code=200, mimetype="application/json")
    except Exception as e:
        logging.error(f"Errore recupero punti squadra: {e}")
        return func.HttpResponse("Errore recupero punti squadra", status_code=500)

#GET/punti/cantante/{cantante_id}
#Descrizione: Recupera il punteggio di un cantante specifico 
@app.route(route="get_punteggi/{cantante_id}", methods=["GET"], auth_level=func.AuthLevel.FUNCTION)
def get_punteggi(req: func.HttpRequest) -> func.HttpResponse:
    cantante_id = int(req.route_params.get('cantante_id'))
    try:
        conn = get_db_connection()
        if conn is None:
            return func.HttpResponse("Errore connessione al DB", status_code=500)
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(punti) as punti_totali FROM Punteggi WHERE cantante_id = ?", cantante_id)
        punti_totali = cursor.fetchone()[0]
        if punti_totali is None:
            punti_totali = 0
        cursor.close()
        conn.close()
        return func.HttpResponse(f'{{"cantante_id": {cantante_id}, "punti_totali": {punti_totali}}}', status_code=200, mimetype="application/json")
    except Exception as e:
        logging.error(f"Errore recupero punti: {e}")
        return func.HttpResponse("Errore recupero punti", status_code=500)








@app.route(route="http_trigger", auth_level=func.AuthLevel.FUNCTION)
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

@app.route(route="http_trigger", auth_level=func.AuthLevel.FUNCTION)
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

@app.route(route="http_trigger", auth_level=func.AuthLevel.FUNCTION)
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