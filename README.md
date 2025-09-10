A chatbot application that allows users to upload PDF documents and ask questions about their content. Built with FastAPI backend and Streamlit frontend, powered by OpenAI's GPT-4.1-mini.

# Features
Document Upload: Upload multiple PDF documents for analysis

Chat Interface: Natural conversation with OpenAI assistant

Context Awareness: The chatbot understands content from uploaded documents

File Management: View and clear uploaded files easily


# Setup instruction 
# Important: Environment Setup
Before running the application, create a `.env` file in the project root with your OpenAI API key:

## Python setup

### 1. Clone the repository
```bash
git clone https://github.com/ShoumanOmar/Applab-chatbot-assignment
```
### 2. Install dependencies (better to create a virtual environment first either using venv or conda)
## Using venv
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
## Using conda
```bash
conda create -n chatbot-env python=3.11
conda activate chatbot-en
```
```bash
pip install -r requirements.txt
```

### 3. Run the backend server
```bash
python backend.py
```
### 4. Simultaneously on another terminal run the frontend server
```bash
streamlit run frontend.py
```
## Docker Setup 
### 1. Download the docker app from https://www.docker.com/products/docker-desktop/

### 2. run the docker builder in the command prompt/terminal as:
```bash
docker-compose up -d
```
### 3. Access the UI from http://localhost:8501

# Important: Environment Setup
Before running the application, create a `.env` file in the project root with your OpenAI API key:

