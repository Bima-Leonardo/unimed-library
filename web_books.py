import streamlit as st
from config import connect_db

def show_books_page():
    # Header User with Mini Logo
    col_logo, col_title = st.columns([1, 5])
    with col_logo:
        try:
            st.image("unimed.png", width=65)
        except:
            pass
    with col_title:
        st.markdown("<h2 style='color: #1e7d32; margin-top: 0;'>📚 UNIMED Digital Library Catalogue</h2>", unsafe_allow_html=True)
        st.write("State University of Medan - Digital Book Repository")
    
    if st.button("🚪 Logout / Exit", type="primary"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.rerun()

    st.write("---")
    
    # --- SIDEBAR BORROW PANEL ---
    st.sidebar.markdown("## 📥 Transaction Panel")
    st.sidebar.write("Fill in details below to Borrow or Return a book.")
    
    name = st.sidebar.text_input("👤 Full Name", placeholder="Type your name...")
    nim = st.sidebar.text_input("🆔 Student ID Number (NIM)", placeholder="Type your NIM...")
    
    st.sidebar.write("---")
    st.sidebar.markdown("### 🔍 Quick Book Search")
    search_keyword = st.sidebar.text_input("Search by Book Title", placeholder="Type keyword...")

    # --- FETCH SYSTEM DATA ---
    conn = connect_db()
    cursor = conn.cursor()
    if search_keyword:
        cursor.execute("SELECT * FROM books WHERE title LIKE %s", ("%" + search_keyword + "%",))
    else:
        cursor.execute("SELECT * FROM books")
    books_list = cursor.fetchall()
    conn.close()

    # --- MAIN CONTENT: BOOK COLLECTION ---
    st.markdown("#### 📖 Active Book Collection")
    if books_list:
        st.dataframe(books_list, column_config={0:"Book ID", 1:"Title", 2:"Author", 3:"Publisher", 4:"Year", 5:"Stock Left"}, use_container_width=True)
    else:
        st.error("🔍 The book you are looking for does not exist in our system.")

    # --- ACTIONS: BORROW & RETURN ---
    st.sidebar.write("---")
    if books_list:
        st.sidebar.markdown("### ⚡ Book Action Target")
        book_options = [f"ID: {b[0]} - {b[1]} (Stock: {b[5]})" for b in books_list]
        selected_book_option = st.sidebar.selectbox("Choose Targeted Book:", book_options)
        selected_book_id = int(selected_book_option.split(" - ")[0].split(": ")[1])
        selected_stock = next(b[5] for b in books_list if b[0] == selected_book_id)

        col1, col2 = st.sidebar.columns(2)
        
        # Borrow Button
        if col1.button("🤝 Borrow", use_container_width=True, type="secondary"):
            if not name or not nim:
                st.sidebar.error("❌ Name & NIM are required!")
            elif not nim.isdigit():
                st.sidebar.error("❌ NIM must be a numeric value!")
            elif selected_stock <= 0:
                st.sidebar.error("❌ Sorry, book stock is empty!")
            else:
                conn = connect_db()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO borrow (book_id, borrow_date, return_date, name, nim) VALUES (%s, NOW(), NULL, %s, %s)", (selected_book_id, name, nim))
                cursor.execute("UPDATE books SET stock = stock - 1 WHERE id=%s", (selected_book_id,))
                conn.commit()
                conn.close()
                st.toast("Book Borrowed Successfully!", icon="✅")
                st.success(f"🎉 **{name}** has successfully borrowed the book. Stock updated!")
                st.rerun()

        # Return Button
        if col2.button("↩️ Return", use_container_width=True):
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM borrow WHERE book_id=%s AND return_date IS NULL ORDER BY id DESC LIMIT 1", (selected_book_id,))
            row = cursor.fetchone()
            
            if not row:
                st.sidebar.error("❌ Active borrow record not found for this book.")
                conn.close()
            else:
                borrow_id = row[0]
                cursor.execute("UPDATE borrow SET return_date = NOW() WHERE id=%s", (borrow_id,))
                cursor.execute("UPDATE books SET stock = stock + 1 WHERE id=%s", (selected_book_id,))
                conn.commit()
                conn.close()
                st.toast("Book Returned Successfully!", icon="↩️")
                st.success("🎉 Book successfully returned to library racks!")
                st.rerun()