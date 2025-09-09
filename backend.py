import os
from fastapi import FastAPI, File, UploadFile, HTTPException, status, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
from openai import OpenAI
import uvicorn
import pypdf
import time


# Configuration for file uploads
UPLOAD_DIR = "./uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- ChatbotService Class ---
class ChatbotService:
    def __init__(self):
        
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        self.client = OpenAI(api_key=key)
        self.conversations: Dict[str, List[Dict[str, str]]] = {}
        # Store document content as a list per session_id to support multiple files
        self.document_contents: Dict[str, List[str]] = {}
        # Store file metadata for each session
        self.document_metadata: Dict[str, List[Dict]] = {}

    async def get_response(self, message: str, session_id: str = "default", has_file: bool = False) -> str:
        # Initialize conversation for session if it doesn't exist
        if session_id not in self.conversations:
            self.conversations[session_id] = []

        # Add the current user message to the conversation history
        self.conversations[session_id].append({"role": "user", "content": message})

        # Prepare messages for OpenAI API call
        messages_for_api = []

        # Add document content to the system message if available for this session
        if session_id in self.document_contents and self.document_contents[session_id]:
            # Combine all document contents for this session
            all_docs_text = "\n\n".join(self.document_contents[session_id])
            
            # Create a list of uploaded files for context
            file_list = ""
            if session_id in self.document_metadata and self.document_metadata[session_id]:
                file_names = [f["filename"] for f in self.document_metadata[session_id]]
                file_list = f"You have access to these uploaded files: {', '.join(file_names)}."
            
            system_message = f"You are a helpful assistant. {file_list} Use the following document content to answer questions: {all_docs_text}"
            messages_for_api.append({"role": "system", "content": system_message})
        else:
            messages_for_api.append({"role": "system", "content": "You are a helpful assistant."})

        # Add conversation history to the API call
        messages_for_api.extend(self.conversations[session_id])

        completion = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages_for_api
        )
        
        bot_response = completion.choices[0].message.content.strip()
        
        # Add the bot's response to the conversation history
        self.conversations[session_id].append({"role": "assistant", "content": bot_response})
        
        return bot_response

    def add_document_content(self, session_id: str, content: str, filename: str):
        # Initialize document list for session if it doesn't exist
        if session_id not in self.document_contents:
            self.document_contents[session_id] = []
        
        # Initialize metadata list for session if it doesn't exist
        if session_id not in self.document_metadata:
            self.document_metadata[session_id] = []
        
        # Append new document content
        self.document_contents[session_id].append(content)
        
        # Store metadata about the uploaded file
        self.document_metadata[session_id].append({
            "filename": filename,
            "upload_time": time.time()
        })
    
    def get_uploaded_files(self, session_id: str) -> List[Dict]:
        """Return list of uploaded files for a session"""
        if session_id in self.document_metadata:
            return self.document_metadata[session_id]
        return []
    
    def clear_documents(self, session_id: str):
        """Clear all uploaded documents for a session"""
        if session_id in self.document_contents:
            self.document_contents[session_id] = []
        if session_id in self.document_metadata:
            self.document_metadata[session_id] = []

# --- FastAPI Application ---
app = FastAPI(
    title="Dumb Chatbot API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Backend is running"}

# Initialize chatbot service
chatbot_service = ChatbotService()

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    has_file: bool = False

class ChatResponse(BaseModel):
    response: str
    session_id: str

class UploadedFilesResponse(BaseModel):
    files: List[Dict]

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...), 
    session_id: str = Form("default")
):
    try:
        # Create session-specific upload directory
        session_upload_dir = os.path.join(UPLOAD_DIR, session_id)
        os.makedirs(session_upload_dir, exist_ok=True)
        
        file_location = os.path.join(session_upload_dir, file.filename)
        with open(file_location, "wb+") as file_object:
            file_object.write(await file.read())

        # Extract text from PDF
        reader = pypdf.PdfReader(file_location)
        text_content = ""
        for page in reader.pages:
            text_content += page.extract_text() or ""
        
        # Add extracted content to chatbot service for the specific session
        chatbot_service.add_document_content(session_id, text_content, file.filename)

        return {
            "status": "success", 
            "message": f"File {file.filename} uploaded and processed.", 
            "filename": file.filename,
            "session_id": session_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload or process file: {e}")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response_content = await chatbot_service.get_response(
            message=request.message,
            session_id=request.session_id,
            has_file=request.has_file
        )
        return ChatResponse(response=response_content, session_id=request.session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files/{session_id}", response_model=UploadedFilesResponse)
async def get_uploaded_files(session_id: str):
    """Get list of uploaded files for a session"""
    files = chatbot_service.get_uploaded_files(session_id)
    return UploadedFilesResponse(files=files)

@app.delete("/files/{session_id}")
async def clear_files(session_id: str):
    """Clear all uploaded files for a session"""
    chatbot_service.clear_documents(session_id)
    return {"status": "success", "message": f"All files cleared for session {session_id}"}

if __name__ == "__main__":
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", 8000))
    uvicorn.run(
        "backend:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )