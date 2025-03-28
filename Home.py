import streamlit as st
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(page_title="TechNest", layout="wide")

st.title("Welcome to TechNest")
st.write("Discover local deals, compare prices, book demos, and get recommendations.")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Login"):
        switch_page("Login")
with col2:
    if st.button("Register"):
        switch_page("Register")
with col3:
    if st.button("Dashboard"):
        switch_page("Dashboard")
