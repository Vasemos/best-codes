import psycopg2
from config import load_config


def connect():
    try:
        params = load_config()
        print("Connecting to the PostgreSQL database...")
        conn = psycopg2.connect(**params)
        print("Connection successful")
        conn.close()
        print("Connection closed")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


if __name__ == '__main__':
    connect()