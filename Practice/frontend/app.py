import streamlit as st
import requests
st.set_page_config(page_title="BookVault", layout="wide")

st.title("BookVault")
st.write("Welcome to my Book Management System")
# single widget rerun the app so include the fields in a Form
st.write("User Registration - New User")
with st.form("User Registration - New User"):
    username = st.text_input("Username") 
    email = st.text_input("Email")
    password = st.text_input("Password",type="password")
    role = st.selectbox("Select role",["user","admin"])
    create_user = st.form_submit_button("Create User")

    if create_user:
        response = requests.post(
            url="http://127.0.0.1:8000/auth/create_user",
            json={
                "username":username,
                "email":email,
                "password":password,
                "role":role
            })
        if response.status_code == 201:
            st.success("User Created successfully")
        else:
            st.error(f"Failed to create user: {response.json().get('detail')}")

st.write("BookVault Login")
with st.form("BookVault Login"):
    username = st.text_input("Username")
    password = st.text_input("Password",type="password")
    login = st.form_submit_button("Login")

    if login:
        response = requests.post(
            url="http://127.0.0.1:8000/auth/login",
            data={
                "username":username,
                "password":password
            }
        )
        if response.status_code == 200:
            token = response.json().get("access_token")
            st.session_state["token"] = token
            st.success("Logged In")
        else:
            st.error(f"Login failed: {response.json().get('detail', 'Unknown error')}")

# using tabs
if "token" in st.session_state:
    st.divider()
    tab1,tab2,tab3,tab4 = st.tabs(["Get Book","Create Book","Update Book","Delete Book"])

    with tab1:
        st.write("Get Books")
        with st.form("Get Books"):
            filter_author = st.text_input("Filter by author")
            filter_category = st.text_input("Filter by category")
            limit_input = st.text_input("Max books to show")
            submit_btn = st.form_submit_button("Search")
            
            if submit_btn:
                # Manual validation (mirrors FastAPI's min_length=3)
                if filter_author and len(filter_author) < 3:
                    st.error("Author name must be at least 3 characters")
                elif filter_category and len(filter_category) < 3:
                    st.error("Category must be at least 3 characters")
                else:
                    params = {
                        "author": filter_author or None,
                        "category": filter_category or None,
                        "limit": int(limit_input) if limit_input else None,
                    }
                    response = requests.get(
                        "http://127.0.0.1:8000/todos/books",
                        params=params,
                        headers={"Authorization": f"Bearer {st.session_state.get('token')}"}
                    )
                    books = response.json()
                    if books:
                        for book in books:
                            with st.container(border=True):
                                st.write(f"**ID:** {book.get('id','N/A')}")
                                st.write(f"**Title:** {book.get('title', 'N/A')}")
                                st.write(f"**Author:** {book.get('author', 'N/A')}")
                                st.write(f"**Category:** {book.get('category', 'N/A')}")
                                st.write(f"**Price** {int(book.get('price',0))}")
                    else:
                        st.info("No books found matching your criteria")

    with tab2:
        st.write("Create Book")
        with st.form("Create new book"):
            title = st.text_input("Title")
            author = st.text_input("Author")
            category = st.text_input("Category")
            price =int(st.number_input("Price"))
            create_book = st.form_submit_button("Create book")
        
            if create_book:
                response = requests.post(
                    url = "http://127.0.0.1:8000/todos/new_book",
                    json = {
                        "title":title,
                        "author":author,
                        "category":category,
                        "price":price                
                    },
                    headers={"Authorization": f"Bearer {st.session_state.get('token')}"}
                ) 
                if response.status_code == 201:
                    book_created = response.json()
                    st.success("Book created successfully")
                    with st.container(border=True):
                        st.write(f"**Title:** {book_created.get("title","N/A")}")
                        st.write(f"**Author:** {book_created.get("author","N/A")}")
                        st.write(f"**Category:** {book_created.get("category","N/A")}")
                        st.write(f"**Price:** Rs.{int(book_created.get("price",0))}")
                else:
                    st.error("Failed to create new book")
    
    with tab3:
        st.write("Update Book")
        with st.form("Update Book"):
            book_id = st.number_input("Id of book", min_value=1, step=1)
            title = st.text_input("Title", placeholder="Leave blank to keep existing")
            author = st.text_input("Author", placeholder="Leave blank to keep existing")
            category = st.text_input("Category", placeholder="Leave blank to keep existing")
            price = st.text_input("Price", placeholder="Leave blank to keep existing")  # text_input so blank = skip
            update_book = st.form_submit_button("Update book")

        if update_book:
            payload = {}
            if title.strip():
                payload["title"] = title.strip()
            if author.strip():
                payload["author"] = author.strip()
            if category.strip():
                payload["category"] = category.strip()
            if price.strip():
                payload["price"] = float(price.strip())

            if not payload:
                st.error("Please provide at least one field to update")
            else:
                response = requests.put(
                    url=f"http://127.0.0.1:8000/todos/update_book/?id={int(book_id)}",
                    json=payload,
                    headers={"Authorization": f"Bearer {st.session_state.get('token')}"}
                )
                if response.status_code == 200:
                    updated_book = response.json()
                    st.success("Book updated successfully")
                    with st.container(border=True):
                        st.write(f"**Title:** {updated_book.get('title', 'N/A')}")
                        st.write(f"**Author:** {updated_book.get('author', 'N/A')}")
                        st.write(f"**Category:** {updated_book.get('category', 'N/A')}")
                        st.write(f"**Price:** Rs.{int(updated_book.get('price', 0))}")
                else:
                    st.error(f"Failed to update book: {response.json().get('detail', 'Unknown error')}")

    with tab4:
        st.write("Delete book")
        with st.form("Delete book"):
            book_id = st.number_input("Book Id",min_value=1)
            delete_book = st.form_submit_button("Delete Book")

            if delete_book:
                response = requests.delete(
                    url=f"http://127.0.0.1:8000/todos/delete_book/{book_id}",
                    # headers={"Authorization":f"Bearer {st.session_state.get("token")}"}
                    headers={"Authorization": f"Bearer {st.session_state.get('token')}"}
                )
                if response.status_code == 200:
                    st.success("Book delete successfully")
                else:
                    st.error("Failed in deleting the book")
            
else:
    st.warning("Please log in first to access the other features")