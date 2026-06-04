import streamlit as str

def get_connection():
    # Mengambil data koneksi otomatis dari Streamlit Secrets Cloud
    conn = str.connection("mysql")
    return conn
