import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        dbname="EGE",
        user="postgres",
        password=os.getenv('DB_PASS'),
        host="localhost",
        port="5432"
    )

def create_subject_table(subject_name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {subject_name} (
            id SERIAL PRIMARY KEY,
            task_number INT,
            url TEXT,
            question TEXT,
            answer TEXT
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def insert_task(subject_name, task_number, url, question, answer):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        f"INSERT INTO {subject_name} (task_number, url, question, answer) VALUES (%s, %s, %s, %s)",
        (task_number, url, question, answer)
    )
    conn.commit()
    cur.close()
    conn.close()
