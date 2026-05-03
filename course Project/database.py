from sqlalchemy import create_engine, text
from flask import flash, redirect, url_for, session
import os

DB_USER = "avnadmin"
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = "mysql-2c884b13-sanskarvijaybhilavade-7834.j.aivencloud.com"
DB_PORT = "12201"
DB_NAME = "defaultdb"

db_connection_string = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
)

engine = create_engine(
    db_connection_string,
    connect_args={"ssl": {"ca": "ca1.pem"}}
)

def add_user_to_db(form_data):
    with engine.connect() as conn:
        query = text("""
            INSERT INTO users1 (email, passwords)
            VALUES (:email, :passwords)
        """)

        conn.execute(query, form_data)
        conn.commit()

def login_user_from_db(email):
    with engine.connect() as conn:
        query = text("""
            SELECT id, email, passwords
            FROM users1
            WHERE email = :email
        """)
        result = conn.execute(query, {"email": email}).fetchone()
        return result

def save_password_to_db(user_id, pass_name, pass_word):
    with engine.connect() as conn:
        
        query = text("""
            INSERT INTO passwords (pass_name, pass_word, user_id)
            VALUES (:pass_name, :pass_word, :user_id)
        """)

        conn.execute(query, {
            "pass_name": pass_name,
            "pass_word": pass_word,
            "user_id": user_id
        })
        conn.commit()


def load_passwords_from_db(user_id):
    with engine.connect() as conn:
        query = text("""
            SELECT pass_name, pass_word
            FROM passwords
            WHERE user_id = :user_id
        """)
        result = conn.execute(query, {"user_id": user_id}).fetchall()
        return result
