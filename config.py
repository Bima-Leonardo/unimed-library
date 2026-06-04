import streamlit as st
import mysql.connector

def connect_db():
    # Mengambil data koneksi otomatis dari Streamlit Secrets Cloud
    secrets = st.secrets["connections"]["mysql"]
    
    conn = mysql.connector.connect(
        host=secrets["host"],
        port=secrets["port"],
        database=secrets["database"],
        user=secrets["username"],
        password=secrets["password"]
    )
    return conn
