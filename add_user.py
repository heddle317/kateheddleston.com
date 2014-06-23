import sys

from app.db.user import create_user
from app.utils.crypto import hash_password


if __name__ == "__main__":
    email = sys.argv[1]
    password = hash_password(sys.argv[2])
    create_user(email, password)
