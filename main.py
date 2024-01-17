from ast import Dict
from typing import List
import logging
import time
from fastapi.responses import JSONResponse
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
import jwt
from fastapi import Depends

app = FastAPI()

logger = logging.getLogger("mytask")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

JWT_SECRET = "mysecret"
JWT_ALGORITHM = "HS256"

# Middlewares
app.add_middleware(
    CORSMiddleware, 
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def redirect_to_https(request, call_next):
    response = await call_next(request)
    return response

def token_response(token:str):
    return {
        "access_token": token
    }


def decodeJWT(token:str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["exp"] >= time.time() else None
    except:
        return {}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    return decodeJWT(token)

fake_users_db = {
    "johndoe": {
        "id":1,
        "username": "johndoe", 
        "full_name": "John Doe",
        "email": "john@example.com",
        "hashed_password": "fakehashedsecret"
    },
    "janedoe": {
        "id":2,
        "username": "janedoe",
        "full_name": "Jane Doe",
        "email": "jane@example.com",
        "hashed_password": "fakehashedsecret2"
    }
}

def fake_password_hasher(raw_password: str):
    return "fakehashed" + raw_password

def authenticate_user(form_data: OAuth2PasswordRequestForm):
    user = fake_users_db.get(form_data.username)
    
    if not user:
        return None

    hashed_password = fake_password_hasher(form_data.password)
    
    if hashed_password != user["hashed_password"]:
        return None

    return user

def create_access_token(user):
    # Generate token payload with user id and expiration
    payload = {
        "sub": user["id"], 
        "exp": time.time() + 3600
    }
    
    # Encode using HS256 algorithm and secret key
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token


@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
      
    # Validate credentials 
    user = authenticate_user(form_data)
    
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token(user)
    return {"access_token": access_token}


# endpoint    
@app.get("/validate_user/")
async def read_user(current_user: dict = Depends(get_current_user)):
    if not current_user: 
        raise HTTPException(status_code=401, detail="Invalid authentication")
        
    return {"msg": "Welcome"}

@app.get("/get_list/")  
def get_list(current_user: dict = Depends(get_current_user), int1: int = Query(..., gt=0), 
    int2: int = Query(..., gt=0),
    limit: int = Query(..., gt=0),
    str1: str = Query(..., min_length=1),
    str2: str = Query(..., min_length=1),
) -> List[str]:
    result = []
    if not current_user:
      raise HTTPException(status_code=401, detail="Invalid authentication")

    try:

        for i in range(1, limit+1):
            if i % int1 == 0 and i % int2 == 0:
                result.append(str1 + str2)
            elif i % int1 == 0: 
                result.append(str1)
            elif i % int2 == 0:
                result.append(str2)
            else:
                result.append(str(i))
    
        return result
    except Exception as e:
        # Log error  
        logger.error(f"Error getting result - {e}")
        return {"error": "An error occurred"}

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    # Custom exception handling for value error
    return JSONResponse({"error": str(exc)}, status_code=400)

# Dictionary to store request counts
request_counts = {}

@app.middleware("http")
async def count_requests(request, call_next):
    path = request.url.path
    request_counts[path] = request_counts.get(path, 0) + 1
    response = await call_next(request)
    return response

# endpoint for statistics
@app.get("/statistics")
def get_statistics(current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid authentication")

    # Find the most used request and its count
    most_used_request = max(request_counts, key=request_counts.get)
    most_used_count = request_counts[most_used_request]

    return {
        "most_used_request": most_used_request,
        "hits_for_most_used_request": most_used_count,
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)