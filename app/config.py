from dotenv import load_dotenv
import os


if not os.getenv("RENDER"):  
    load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES",30))
DATABASE_URL = os.getenv("DATABASE_URL")
