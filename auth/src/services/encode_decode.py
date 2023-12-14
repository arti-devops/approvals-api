import uuid
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status

from ..services.environnement import env
from ..services.oauth2_scheme import oauth2_scheme
from ..services.token_blacklist import token_blacklist

# Function to generate a unique JWT ID (jti)
def generate_jti():
    return str(uuid.uuid4())

# Function to decode JWT token
def decode_token(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Decode a JWT token and return its payload.

    Args:
        token (str, optional): The JWT token to decode. Defaults to using the 'oauth2_scheme' dependency.

    Returns:
        dict: The decoded payload of the JWT token.

    returns:
        HTTPException: returnd if credentials are invalid or if the token has expired.
    """
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    expired_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token has expired",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, env("SECRET_KEY"), algorithms=[env("ALGORITHM")])

        # Check if the 'jti' claim is in the payload and if the token is in the blacklist
        if "jti" not in payload or payload["jti"] in token_blacklist:
            raise credentials_exception

        return payload
    except jwt.ExpiredSignatureError:
        raise expired_exception
    except JWTError:
        raise credentials_exception
