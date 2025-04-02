import jwt
import datetime
from fastapi import FastAPI, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from db import get_db_connection
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

# Secret key for JWT
SECRET_KEY = "your_secret_key"  # Replace with a secure secret key
ALGORITHM = "HS256"

app = FastAPI()

# Function to generate a JWT token
def create_jwt_token(username: str):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token valid for 1 hour
    payload = {
        "sub": username,
        "exp": expiration
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# Function to decode and verify the JWT token
def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/protected/")
async def protected_route(token: str):
    user_data = verify_jwt_token(token)
    return {"message": "Access granted", "user": user_data}


# HTML Form as a Python function (with token verification input)
def login_form():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
</head>
<body>
    <h2>Login Page</h2>
    <form action="/login/" method="post">
        <label for="username">Username:</label><br>
        <input type="text" id="username" name="username" required><br><br>
        <label for="password">Password:</label><br>
        <input type="password" id="password" name="password" required><br><br>
        <input type="submit" value="Login">
    </form>

    <h2>Check JWT Token</h2>
    <form action="/check-token/" method="post">
        <label for="token">Enter JWT Token:</label><br>
        <input type="text" id="token" name="token" required><br><br>
        <input type="submit" value="Verify Token">
    </form>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
async def login_page():
    return login_form()

@app.post("/login/")
async def login(username: str = Form(...), password: str = Form(...)):
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        cursor.close()
        connection.close()

        if user:
            token = create_jwt_token(username)
            return {"message": "Login successful", "token": token}
        else:
            raise HTTPException(status_code=400, detail="Invalid credentials")
    else:
        raise HTTPException(status_code=500, detail="Database connection failed")

# Endpoint to check a JWT token
@app.post("/check-token/")
async def check_token(token: str = Form(...)):
    try:
        payload = verify_jwt_token(token)
        return {"message": "Token is valid", "user": payload}
    except HTTPException as e:
        return {"message": str(e.detail)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
