#!/usr/bin/python
import psycopg2
import time
import os
import sys
import pprint
# Assigning the environment variables
i_w_d = os.environ['INIT_WAIT_DELAY']   # Time period (in sec) b/w retries for DB init check
i_r_c=os.environ['INIT_RETRY_COUNT']      # No of retries for DB init check
l_p_s=os.environ['LIVENESS_PERIOD_SECONDS'] # Time period (in sec) b/w liveness checks
l_t_s=os.environ['LIVENESS_TIMEOUT_SECONDS']  # Time period (in sec) b/w retries for db_connect failure
l_r_c=os.environ['LIVENESS_RETRY_COUNT']     # No of retries after a db_connect failure before declaring liveness fail
ns=os.environ["NAMESPACE"]  # Namespace in which Postgres is Running
sv=os.environ["SERVICE_NAME"] #Service name of Postgres
user=os.environ["USER"] #User name of Postgres
db=os.environ["DATABASE"] #Database name of postgres
password=os.environ["PASSWORD"] #Password for the postgres db
port=os.environ["PORT"] #Port value of Postgres service

def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        url = ""+sv+"."+ns+"."+"svc.cluster.local"
        conn = psycopg2.connect(host=url, database=db, port=port, user=user, password=password)
        # create a cursor
        cur = conn.cursor()
        
        # execute a statement
        cur.execute('SELECT version()')
 
        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        # close the communication with the PostgreSQL
        cur.close()
        return 1
    except (Exception, psycopg2.DatabaseError) as error:
        print('Liveness Failed')
        return 0
    finally:
        if conn is not None:
            conn.close()

#checking the database status
def database_check():
    for i in range(1,int(i_r_c)):
        x=connect()
        if x==0:
            connect()
            print("fail",flush=True)
        else:
            print("pass", x,flush=True)
            break
        time.sleep(int(i_w_d))

def retry_connection():
    for y in range(1,int(l_r_c)):
       z=connect()
       if z==1:
           return z
       time.sleep(int(l_t_s))
    if z==0:
        return z

def liveness_check():
    while True:
        try:
            url = ""+sv+"."+ns+"."+"svc.cluster.local"
            conn = psycopg2.connect(host=url, database=db, port=port, user=user, password=password)
            # create a cursor
            cur = conn.cursor()
            print("liveness Running",flush=True)
            # sys.stdout.flush()
        except Exception as error:
            print("liveness Failed" ,flush=True)
            # sys.stdout.flush()
            z=retry_connection()
            if z==0:
                break   
        time.sleep(int(l_p_s))

if __name__ == '__main__':
    database_check()
    liveness_check()