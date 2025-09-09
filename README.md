A chatbot application that allows users to upload PDF documents and ask questions about their content. Built with FastAPI backend and Streamlit frontend, powered by OpenAI's GPT-4.1.

# Features
Document Upload: Upload multiple PDF documents for analysis

Chat Interface: Natural conversation with OpenAI assistant

Context Awareness: The chatbot understands content from uploaded documents

File Management: View and clear uploaded files easily

# Setup instruction 
## Python setup

### 1. Clone the repository
```bash
git clone https://github.com/ShoumanOmar/Applab-chatbot-assignment

### 2. Install dependencies (better to create a virtual environment first either using venv or conda)
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Using conda
conda create -n chatbot-env python=3.9
conda activate chatbot-en
pip install -r requirements.txt


### 3. Run the backend server
python backend.py

### 4. Simultaneously on another terminal run the frontend server
streamlit run frontend.py

## Docker Setup 
### 1. Download the docker app from https://www.docker.com/products/docker-desktop/

### 2. run docker-compose up -d

### 3. Access the UI from http://localhost:8501


