from passlib.context import CryptContext

USERS = dict()
TASKS = dict()
pwd_context = CryptContext(schemes="bcrypt")

def hash_pass(password: str) -> str:
    hashed_password = pwd_context.hash(password)
    return hashed_password


def verify_pass(plain_pass: str, hashed_pass: str) -> bool:
    return pwd_context.verify(plain_pass, hashed_pass)