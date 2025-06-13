from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import List
import psycopg2



SECRET_KEY = "muzifa"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def get_db_connections():
    return psycopg2.connect(
        dbname="ecommerce_bx3f",
        user="muzifa",
        password="QZ1rEEY6pRiaYdtGNAsiNoW5lqmp0oY2",
        host="dpg-d14hvru3jp1c73begj3g-a.singapore-postgres.render.com",
        port="5432"  
    )


app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#print(pwd_context.hash("himuzifa"))



def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str):
    conn = get_db_connections()
    cursor = conn.cursor()

    cursor.execute("SELECT user_name, user_password FROM users WHERE user_name = %s", (username,))
    result = cursor.fetchone()
    print(result) 

    cursor.close()
    conn.close()

    if result is None:
        return False

    user_name, user_password = result

    if not verify_password(password, user_password):
        return False
    '''if not pwd_context.verify(password, user_password):
        return False'''

    return {"username": user_name}

    

'''def authenticate_user(username: str, password: str):
    conn=get_db_connections()
    cursor=conn.cursor()
    users=cursor.execute("Select * from users")
    for user in users:
        if user.user_name==username:

    #user = var.get(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return False
    return user'''

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

class User(BaseModel):
    username:str
    password:str

@app.get("/")
def printit():
    return {
        "hi":200
    }


@app.post("/tokens")
def login(form_data:User):
    '''return {
        "hi":200
    }'''
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token,"auth":True, "token_type": "bearer"}
 
@app.post("/register", status_code=201)
def register(user: User):
    conn = get_db_connections()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE user_name = %s", (user.username,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = pwd_context.hash(user.password)
    cursor.execute("INSERT INTO users (user_name, user_password) VALUES (%s, %s)", (user.username, hashed_password))
    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "User registered successfully"}

from fastapi import Security

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"username": username}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/protected")
def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Hello {current_user['username']}, you're authorized!"}


