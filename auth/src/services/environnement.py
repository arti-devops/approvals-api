import os

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

def env(variable: str, default=None, cast=None):
    value = os.getenv(variable, default)

    if value is not None and cast is not None:
        try:
            value = cast(value)
        except (ValueError, TypeError):
            # Handle the case where casting fails
            raise ValueError(f"Failed to cast '{value}' to {cast.__name__}")

    return value
