import streamlit as st
import sqlite3
from config import connect_db
from web_admin import show_admin
from web_books import show_books_page

# ==========================================
# 1. PANCINGAN OTOMATIS PEMBUAT DATABASE SQLITE
# ==========================================
def inisialisasi_database_otomatis():
    conn = sqlite3.connect("digital_library.db")
    cursor = conn.cursor()
    
    # Membuat Tabel Akun Pengguna (User)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)
    
    # Membuat Tabel Katalog Buku
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        author TEXT,
        year INTEGER,
        status TEXT DEFAULT 'Available'
    )
    """)
    
    # Membuat Tabel Transaksi Peminjaman
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT,
        student_nim TEXT,
        book_title TEXT,
        action_type TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Memasukkan Akun Admin Dummy bawaan untuk Login awal kamu
    cursor.execute("""
    INSERT OR IGNORE INTO users (id, username, password, role) 
    VALUES (1, 'bima', 'unimed123', 'admin')
    """)
    
    # Memasukkan beberapa Buku Dummy awal biar web tidak kosong melompong
    cursor.execute("SELECT COUNT(*) FROM books")
    if cursor.fetchone()[0] == 0:
        buku_awal = [
            ('Struktur Data Python', 'Dr. Edi Syahputra', 2022, 'Available'),
            ('Sistem Informasi Manajemen', 'Prof. Dian Utami', 2021, 'Available'),
            ('Dasar-Dasar Pemrograman Web', 'Bima Leonardo', 2024, 'Available'),
            ('Kalkulus & Aljabar Linear', 'Jurusan Matematika UNIMED', 2020, 'Available')
        ]
        cursor.executemany("INSERT INTO books (title, author, year, status) VALUES (?, ?, ?, ?)", buku_awal)
        
    conn.commit()
    conn.close()

# Jalankan inisialisasi database di server cloud
inisialisasi_database_otomatis()

# ==========================================
# 2. SISTEM AUTENTIKASI LOGIN UTAMA
# ==========================================
def cek_login_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()
    # Mencari kecocokan username dan password di tabel users
    cursor.execute("SELECT role FROM users WHERE username = ? AND password = ?", (username, password))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# Setelan Layout Judul Browser Web
st.set_page_config(page_title="UNIMED Digital Library", layout="wide")

# Inisialisasi status sesi (Session State) jika belum ada
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None

# ==========================================
# 3. KONTROL TAMPILAN HALAMAN (NAVIGASI)
# ==========================================
if not st.session_state.logged_in:
    # TAMPILAN FORM LOGIN JIKA BELUM MASUK
    st.markdown("<h2 style='text-align: center; color: #2E7D32;'>🎓 UNIMED Digital Library Login</h2>", unsafe_allow_html=True)
    st.write("Silakan masuk menggunakan akun perpustakaan digital Anda.")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username_input = st.text_input("Username / NIM")
            password_input = st.text_input("Password", type="password")
            tombol_login = st.form_submit_button("Masuk Aplikasi")
            
            if tombol_login:
                role_ditemukan = cek_login_user(username_input, password_input)
                if role_ditemukan:
                    st.session_state.logged_in = True
                    st.session_state.user_role = role_ditemukan
                    st.success("Login Berhasil! Membuka sistem...")
                    st.rerun()
                else:
                    st.error("Username atau Password salah! Silakan periksa kembali.")
else:
    # TAMPILAN JIKA SUDAH BERHASIL LOGIN
    if st.session_state.user_role == "admin":
        # Jika akun yang masuk bertindak sebagai admin, buka file web_admin.py
        show_admin()
    else:
        # Jika akun biasa/mahasiswa, buka file katalog biasa
        show_books_page()
