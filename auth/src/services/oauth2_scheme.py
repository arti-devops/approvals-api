from fastapi.security import OAuth2PasswordBearer

# Define OAuth2PasswordBearer for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")