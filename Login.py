import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

st.set_page_config(layout="centered", initial_sidebar_state="collapsed")

# Firebase Setup
if not firebase_admin._apps:
    cred = credentials.Certificate(st.secrets["firestore"].to_dict())
    firebase_admin.initialize_app(cred)
db = firestore.client()

# Store credentials securely in session state
if 'db' not in st.session_state:
    st.session_state['db'] = db


def main():
    st.markdown('<div style="display: flex; justify-content: center;"><h1>FCR AI Tool</h1></div>',unsafe_allow_html=True)

    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    if st.button("Sign In"):
        st.session_state['agent_name'] = username
        st.switch_page('pages/AI_Agent_Assist.py')


if __name__ == "__main__":
    main()