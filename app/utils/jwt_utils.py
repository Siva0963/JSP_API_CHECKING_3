from jose import jwt
from datetime import datetime, timedelta

ALGORITHM = "RS256"

# Read private key
with open("private_key.pem", "r") as f:
    PRIVATE_KEY = f.read()


def create_access_token(data: dict):

    expire = datetime.utcnow() + timedelta(hours=24)

    data.update({"exp": expire})

    token = jwt.encode(data, PRIVATE_KEY, algorithm=ALGORITHM)

    return token