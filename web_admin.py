import streamlit as st
from config import connect_db

def load_stats():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM books")
        total_books = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM borrow WHERE return_date IS NULL")
        active_borrow = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM borrow")
        total_history = cursor.fetchone()[0]
        conn.close()
        return total_books, active_borrow, total_history
    except:
        return 0, 0, 0

def show_admin():
    # Header Admin with Mini Logo Row
    col_logo, col_title = st.columns([1, 5])
    with col_logo:
        try:
            st.image("unimed.png", width=65)
        except:
            pass
    with col_title:
        st.markdown("<h2 style='color: #ef6c00; margin-top: 0;'>⚙️ Admin Dashboard</h2>", unsafe_allow_html=True)
        st.write("Welcome to the Library Management Panel.")
    
    if st.button("🚪 Logout from Admin", type="primary"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.rerun()

    st.write("---")

    # --- STATS CARDS ---
    total_books, active_borrow, total_history = load_stats()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="📚 Total Book Titles", value=total_books)
    with col2:
        st.metric(label="🔄 Actively Borrowed", value=active_borrow, delta=f"{active_borrow} Active", delta_color="inverse")
    with col3:
        st.metric(label="📝 Total Transactions", value=total_history)

    st.write("---")
    
    # --- BOOK MANAGEMENT (CRUD) ---
    st.markdown("### 🛠️ Manage Books Database (CRUD)")
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books")
    books_data = cursor.fetchall()
    conn.close()

    # Dropdown Options
    options = ["➕ Add New Book"] + [f"ID: {b[0]} - {b[1]}" for b in books_data]
    selected_option = st.selectbox("Select a book to edit/delete:", options)

    b_id, title, author, publisher, year, stock = "", "", "", "", 2026, 0
    is_edit = selected_option != "➕ Add New Book"

    if is_edit:
        b_id = int(selected_option.split(" - ")[0].split(": ")[1])
        selected_book = next(b for b in books_data if b[0] == b_id)
        title = selected_book[1]
        author = selected_book[2]
        publisher = selected_book[3]
        year = selected_book[4]
        stock = selected_book[5]

    # Input Form
    with st.form("book_form", clear_on_submit=not is_edit):
        st.markdown("**Book Information Fields:**")
        t_input = st.text_input("Book Title *", value=title)
        a_input = st.text_input("Author Name *", value=author)
        p_input = st.text_input("Publisher", value=publisher)
        y_input = st.number_input("Year of Publish", value=int(year), min_value=1800, max_value=2026)
        s_input = st.number_input("Stock Available *", value=int(stock), min_value=0)
        
        st.write("")
        col_btn1, col_btn2, _ = st.columns([1, 1, 2])
        
        if not is_edit:
            submit = col_btn1.form_submit_button("💾 Save New Book")
            if submit:
                if not t_input or not a_input:
                    st.error("⚠️ Title and Author are required fields!")
                else:
                    conn = connect_db()
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO books (title, author, publisher, year_publish, stock) VALUES (%s, %s, %s, %s, %s)",
                                   (t_input, a_input, p_input if p_input else "-", y_input, s_input))
                    conn.commit()
                    conn.close()
                    st.success("🎉 New book successfully added to database!")
                    st.rerun()
        else:
            update = col_btn1.form_submit_button("✏️ Update Data")
            delete = col_btn2.form_submit_button("🗑️ Delete Book")
            
            if update:
                conn = connect_db()
                cursor = conn.cursor()
                cursor.execute("UPDATE books SET title=%s, author=%s, publisher=%s, year_publish=%s, stock=%s WHERE id=%s",
                               (t_input, a_input, p_input, y_input, s_input, b_id))
                conn.commit()
                conn.close()
                st.success("✨ Book data updated successfully!")
                st.rerun()
                
            if delete:
                conn = connect_db()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM books WHERE id=%s", (b_id,))
                conn.commit()
                conn.close()
                st.warning("💥 Book has been removed from the system!")
                st.rerun()

    # --- INVENTORY TABLE ---
    st.write("")
    st.markdown("### 📊 Book Inventory List")
    if books_data:
        st.dataframe(books_data, column_config={0:"ID", 1:"Book Title", 2:"Author", 3:"Publisher", 4:"Year", 5:"Stock Current"}, use_container_width=True)
    else:
        st.info("The books database is currently empty.")

    # --- LOG TRANSACTIONS ---
    st.write("---")
    st.markdown("### 📋 Library Borrowing Log History")
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, book_id, name, nim, borrow_date, return_date FROM borrow ORDER BY id DESC")
    history_data = cursor.fetchall()
    conn.close()
    
    if history_data:
        st.dataframe(history_data, column_config={0:"Tx ID", 1:"Book ID", 2:"Student Name", 3:"NIM", 4:"Borrow Date", 5:"Return Date"}, use_container_width=True)
    else:
        st.info("No transaction history found.")