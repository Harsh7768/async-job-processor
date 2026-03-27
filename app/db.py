import psycopg


def get_connection():
    return psycopg.connect(
        dbname="job_db",
        user="postgres",
        password="1234",
        host="localhost",
        port="5432"
    )