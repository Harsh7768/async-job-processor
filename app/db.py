import psycopg
import os


def get_connection():
    return psycopg.connect(os.getenv("DATABASE_URL"))