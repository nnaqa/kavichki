# -*- coding: utf-8 -*-

import psycopg2
from config import config


def connect():
    """ Connect to the PostgreSQL database server """
    cur = None
    conn = None
    try:
        # read connection parameters
        params = config()
        # connect to the PostgreSQL server
        print()
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        # create a cursor
        cur = conn.cursor()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    return cur, conn

def teardown(conn):
    """ Close the connection with database """
    if conn is not None:
        conn.close()
        print()
        print('Database connection closed.')