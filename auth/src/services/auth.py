#services/auth.py
from jose import jwt
from base64 import b64decode
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from fastapi.responses import JSONResponse

from ..services.encode_decode import generate_jti
from ..services.token_blacklist import token_blacklist
from ..services.file_reader_csv import read_userdata_csv

from ..services.environnement import env

def process_login(authorization, collection) -> dict:
    """
    Process user login based on the provided authorization credentials.

    Args:
        authorization (str): The authorization header containing credentials.

    Returns:
        dict: A dictionary containing an access token, token type, and expiration time.

    Raises:
        CredentialsException: Raised if the provided credentials are invalid or the user is not found.
    """
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials: " + authorization,
        headers={"WWW-Authenticate": "Bearer"},
    )

    filename_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Can't find user in the database",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        scheme, credentials = authorization.split()
        if scheme.lower() != "basic":
            raise credentials_exception

        decoded_credentials = b64decode(credentials).decode("utf-8")
        username, password = decoded_credentials.split(":", 1)

        # Load users from the CSV file
        #users = read_userdata_csv(env("FILENAME"))
        users = collection.find({})
        # print(list(users))

        # Check if the provided username and password match any user in the file
        for user in users:
            print(user)
            if user["username"] == username and user["password"] == password:
                # User is valid, generate a token with a TOKEN_EXPIRE-minute expiration time
                expiration_time = datetime.utcnow() + timedelta(minutes=env("TOKEN_EXPIRE", cast=int))
                # Add abilities
                abilities = []
                if user["role"] == "admin":
                    abilities = [
                        {
                            "action": 'manage',
                            "subject": 'all'
                        }
                    ]

                # Generate a unique JWT ID (jti)
                jti = generate_jti()

                token_data = {
                    "sub": username,
                    "jti": jti,
                    "fullName": user["username"],
                    "exp": expiration_time,
                    "role": user["role"],
                    "avatar": "/images/avatars/avatar-2.png",
                    "abilities": abilities,
                }

                token = jwt.encode(token_data, env("SECRET_KEY"), algorithm=env("ALGORITHM"))
                return {"access_token": token, "token_type": "bearer", "expires_in": env("TOKEN_EXPIRE",cast=int)*60}

        # If no matching user is found
        raise credentials_exception
    except Exception as e:
        raise filename_exception

def process_logout(current_user):
    """
    Endpoint to revoke the current user's token (logout).
    """
    jti = current_user.get("jti")
    if jti:
        token_blacklist.add(jti)
    return {"message": "Logout successful"}
        