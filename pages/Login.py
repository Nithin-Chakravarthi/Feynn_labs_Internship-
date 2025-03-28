import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from db_utils import authenticate_user

st.set_page_config(page_title="Login")
st.title("Login")

role = st.selectbox("Select Role", ["Customer", "Retailer"])
email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("Login"):
    user_id = authenticate_user(email, password, role)
    if user_id:
        st.session_state["logged_in"] = True
        st.session_state["role"] = role
        st.session_state["user_id"] = user_id
        st.success("Logged in successfully!")
        switch_page("Dashboard")
    else:
        st.error("Invalid credentials!")

st.write("Don't have an account?")
if st.button("Go to Register"):
    switch_page("Register")
