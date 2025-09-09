import streamlit as st
import requests
import time
import os

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = f"session_{int(time.time())}"
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
    if "upload_mode" not in st.session_state:
        st.session_state.upload_mode = False

def check_backend_connection():
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=1)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def upload_document(uploaded_file):
    try:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        data = {"session_id": st.session_state.session_id}
        response = requests.post(f"{BACKEND_URL}/upload", files=files, data=data, timeout=30)
        if response.status_code == 200:
            # Update the uploaded files list
            get_uploaded_files()
            return response.json()
        return None
    except requests.exceptions.RequestException:
        return None

def get_uploaded_files():
    try:
        response = requests.get(f"{BACKEND_URL}/files/{st.session_state.session_id}", timeout=5)
        if response.status_code == 200:
            st.session_state.uploaded_files = response.json()["files"]
        else:
            st.session_state.uploaded_files = []
    except requests.exceptions.RequestException:
        st.session_state.uploaded_files = []

def clear_uploaded_files():
    try:
        response = requests.delete(f"{BACKEND_URL}/files/{st.session_state.session_id}", timeout=5)
        if response.status_code == 200:
            st.session_state.uploaded_files = []
            return True
        return False
    except requests.exceptions.RequestException:
        return False

def send_message(message: str, has_file: bool = False):
    try:
        payload = {"message": message, "session_id": st.session_state.session_id, "has_file": has_file}
        response = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()["response"]
        return f"Error: {response.json().get('detail', 'Unknown error')}"
    except requests.exceptions.RequestException as e:
        return f"Connection error: {str(e)}"

def display_file_message(file_name):
    return f"📎 {file_name}"

def main():
    init_session_state()

    st.title("Chatbot")

    if not check_backend_connection():
        st.write("Cannot connect to backend.")
        return

    # Get uploaded files on initial load
    if not st.session_state.uploaded_files:
        get_uploaded_files()

    # Display chat messages
    chat_container = st.container(height=400)
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                if message["type"] == "text":
                    st.markdown(message["content"])
                else:  # file message
                    st.markdown(f"📎 {message['content']}")

    # Create a container for the input area
    input_container = st.container()
    
    with input_container:
        # Use columns to position the attach button next to the input
        col1, col2 = st.columns([6, 1])
        
        with col1:
            if st.session_state.upload_mode:
                uploaded_file = st.file_uploader(
                    "Choose a PDF file", 
                    type=["pdf"], 
                    label_visibility="collapsed",
                    key="file_uploader"
                )
                if uploaded_file is not None:
                    if uploaded_file.size <= MAX_FILE_SIZE:
                        # Add file message to chat
                        file_msg = display_file_message(uploaded_file.name)
                        st.session_state.messages.append({"role": "user", "content": uploaded_file.name, "type": "file"})
                        
                        # Upload file to backend
                        with st.spinner("Uploading file..."):
                            result = upload_document(uploaded_file)
                            if result:
                                # Get response from chatbot about the uploaded file
                                response = send_message(f"I've uploaded a file named {uploaded_file.name}.", True)
                                st.session_state.messages.append({"role": "assistant", "content": response, "type": "text"})
                                st.success("File uploaded successfully!")
                            else:
                                st.error("File upload failed.")
                        
                        # Reset upload mode
                        st.session_state.upload_mode = False
                        st.rerun()
                    else:
                        st.error("File too large. Maximum size is 10MB.")
            else:
                # Regular text input
                user_input = st.chat_input("Ask a question...", key="text_input")
                if user_input:
                    # Add user message to chat history
                    st.session_state.messages.append({"role": "user", "content": user_input, "type": "text"})
                    
                    # Get response from chatbot
                    with st.spinner("Thinking..."):
                        response = send_message(user_input)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response, "type": "text"})
                    st.rerun()
        
        with col2:
            # Attach button
            if st.button("📎", help="Attach file", key="attach_button"):
                st.session_state.upload_mode = not st.session_state.upload_mode
                st.rerun()

    # Sidebar with uploaded files and controls
    with st.sidebar:
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.rerun()
            
        if st.button("Clear All Files"):
            if clear_uploaded_files():
                st.success("All files cleared!")
                st.rerun()
            else:
                st.error("Failed to clear files.")
        
        # Display uploaded files
        if st.session_state.uploaded_files:
            st.subheader("Uploaded Files")
            for file in st.session_state.uploaded_files:
                st.text(f"📎 {file['filename']}")
        else:
            st.info("No files uploaded yet.")

if __name__ == "__main__":
    main()