import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from db_utils import register_user

st.set_page_config(page_title="Register")
st.title("Register")

role = st.selectbox("Select Role", ["Customer", "Retailer"])
username = st.text_input("Username")
email = st.text_input("Email")
password = st.text_input("Password", type="password")
location = st.text_input("Location (City/Area)")

if st.button("Register"):
    if register_user(username, email, password, role, location):
        st.success("Registration successful! Please log in.")
        switch_page("Login")
    else:
        st.error("User already exists!")

st.write("Already have an account?")
if st.button("Go to Login"):
    switch_page("Login")
