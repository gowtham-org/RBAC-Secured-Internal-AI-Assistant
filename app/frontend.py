import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import time
import os

try:
    API_URL = st.secrets["API_URL"]
except Exception:
    API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="🧠 Role-Based Chatbot", layout="centered")


# ------------------------------
# Initialize session state
# ------------------------------
if "user" not in st.session_state:
    st.session_state.user = None
if "auth" not in st.session_state:
    st.session_state.auth = None
if "history" not in st.session_state:
    st.session_state.history = []


# ------------------------------
# Sidebar: Login Panel
# ------------------------------
with st.sidebar:
    st.title("🔐 Login Panel")

    if st.session_state.user is None:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            try:
                response = requests.get(
                    f"{API_URL}/login",
                    auth=HTTPBasicAuth(username, password),
                    timeout=10,
                )
            except requests.exceptions.RequestException:
                st.error("🚫 Backend unreachable — the cluster may be offline.")
            else:
                if response.status_code == 200:
                    user_data = response.json()
                    st.session_state.user = {
                        "username": username,
                        "role": user_data["role"],
                    }
                    st.session_state.auth = HTTPBasicAuth(username, password)
                    st.success(f"Welcome, {username}!")
                    st.rerun()
                elif response.status_code == 401:
                    st.error("❌ Invalid credentials. Please try again.")
                else:
                    st.error(f"❌ Unexpected server response ({response.status_code}).")

    else:
        st.markdown(f"**👤 Logged in as:** `{st.session_state.user['username']}`")
        st.markdown(f"**🧾 Role:** `{st.session_state.user['role']}`")

        if st.button("Logout"):
            st.session_state.user = None
            st.session_state.auth = None
            st.session_state.history = []
            st.rerun()


# ------------------------------
# Main Chat Interface
# ------------------------------
st.title("🤖 AI Assistant")
st.caption("Ask me anything about your documents.")

if st.session_state.user:

    if len(st.session_state.history) == 0:
        st.session_state.history.append((
            "initial_greeting",
            "Hello! I am your AI assistant. How can I help you today?"
        ))

    with st.expander("📘 Role & Access Explanation", expanded=False):
        user_role = st.session_state.user["role"].lower()
        if "c-levelexecutives" in user_role:
            st.info("Unfiltered access — full visibility (C-Level Executives).")
        elif "employee" in user_role:
            st.info("Filtered access — only general category documents (Employee).")
        else:
            st.info(f"Filtered by department: `{user_role}`.")

    with st.container():
        for i, (question, answer) in enumerate(st.session_state.history[-10:]):
            if question == "initial_greeting":
                with st.chat_message("ai"):
                    st.markdown(answer)
            else:
                with st.chat_message("user"):
                    st.markdown(question)
                with st.chat_message("ai"):
                    st.markdown(answer)

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"👍 Helpful {i}", key=f"yes_{i}"):
                            st.toast("You found this helpful!", icon="👍")
                    with col2:
                        if st.button(f"👎 Not Helpful {i}", key=f"no_{i}"):
                            st.toast("You found this unhelpful", icon="👎")

    user_input = st.chat_input("💬 Type your question here")

    if user_input:
        st.chat_message("user").markdown(user_input)

        with st.chat_message("ai"):
            with st.spinner("🤖 Thinking..."):
                try:
                    response = requests.post(
                        f"{API_URL}/chat",
                        json={"message": user_input},
                        auth=st.session_state.auth,
                        timeout=60,
                    )
                except requests.exceptions.RequestException:
                    st.error("🚫 Backend unreachable — the cluster may be offline.")
                else:
                    if response.status_code == 200:
                        reply = response.json().get("response", "No response.")

                        typed_text = ""
                        container = st.empty()
                        for word in reply.split(" "):
                            typed_text += word + " "
                            container.markdown(typed_text)
                            time.sleep(0.02)

                        st.session_state.history.append((user_input, reply))
                    elif response.status_code == 401:
                        st.error("🔒 Session expired. Please log in again.")
                        st.session_state.user = None
                        st.session_state.auth = None
                        st.rerun()
                    else:
                        st.error(f"❌ Server error ({response.status_code}).")

else:
    st.info("🔐 Please log in from the sidebar to continue.")