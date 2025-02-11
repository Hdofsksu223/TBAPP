import os
import psycopg2
from psycopg2 import sql


def get_db_connection():
    try:
        return psycopg2.connect(
            host="localhost",
            database="tebedata",
            user="postgres",
            password="admin",  # Add actual password
            port="5432"
        )
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        return None


if __name__ == "__main__":
    get_db_connection()
