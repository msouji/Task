# Task
# FastAPI Project

## Build Instructions

This project requires Python 3.12 or higher. It is recommended to use a virtual environment for development.

### 1. Clone the Repository

```bash
git clone https://github.com/msouji/Task
cd Task

### 2. Create and Activate Virtual Environment

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Linux/Mac
venv\Scripts\activate  # On Windows

### 3. Install Dependencies

pip install -r requirements.txt

### 4. Run the fast api server

uvicorn main:app --reload

The server will be running at http://127.0.0.1:8000.

6. Access API Documentation

http://127.0.0.1:8000/docs


