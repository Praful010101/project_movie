import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask, request
from datetime import datetime, timezone

load_dotenv()  

app = Flask(__name__)
url = os.environ.get("DATABASE_URL")  
connection = psycopg2.connect(url)


CREATE_DETAILS_TABLE = (
    "CREATE TABLE IF NOT EXISTS details (movie_id int not null, movie VARCHAR(10), poster_path VARCHAR(10), language VARCHAR(10) , overview VARCHAR(10), release_date date, CONSTRAINT movie_id_pk PRIMARY KEY (movie_id));"
)

INSERT_DETAILS = (
    "INSERT INTO details (movie_id, movie, poster_path, language, overview, release_date) VALUES (%s, %s, %s, %s, %s, %s) RETURNING movie_id;"
)

movie = """SELECT movie FROM details WHERE movie_id = (%s)"""

path = """SELECT poster_path FROM details WHERE movie_id = (%s)"""

language = """SELECT language FROM details WHERE movie_id = (%s)"""

overview = """SELECT overview FROM details WHERE movie_id = (%s)"""

date = """SELECT release_date FROM details WHERE movie_id = (%s)"""




@app.post("/v1/movie")
def create_movie():
    data = request.get_json()
    movie_id = data["movie_id"]
    movie = data["movie"]
    poster_path = data["poster_path"]
    language = data["language"]
    overview = data["overview"]
    # release_date = data["release_date"]
    try:
        release_date = datetime.strptime(data["release_date"], "%m-%d-%Y %H:%M:%S")
    except KeyError:
        release_date = datetime.now(timezone.utc)
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_DETAILS_TABLE)
            cursor.execute(INSERT_DETAILS, (movie_id, movie, poster_path, language, overview, release_date,))
            movie_id = cursor.fetchone()[0]
    return {"id": movie_id, "message": "Movie created."}, 201

@app.get("/v1/movie/<int:movie_id>")
def get_movie_all(movie_id):
    args = request.args
    details = args.get("details")
    # if details is None:
    #     return "No movie created"
    # else:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(movie, (movie_id,))
            movie_title = cursor.fetchone()[0]
            cursor.execute(path, (movie_id,))
            poster_path = cursor.fetchone()[0]
            cursor.execute(language, (movie_id,))
            movie_language = cursor.fetchone()[0]
            cursor.execute(overview, (movie_id,))
            movie_overview = cursor.fetchone()[0]
            cursor.execute(date, (movie_id,))
            release_date = cursor.fetchone()[0]
    return {"movie": movie_title, "poster_path": poster_path, "language": movie_language, "overview": movie_overview, "release_date": release_date} 

