import sys

from app.db.user import get_or_create_user
from app.db.user import get_verified_user
from app.db.user import update_user
from app.utils.crypto import hash_password


if __name__ == "__main__":
    email = sys.argv[1]
    password = sys.argv[2]
    user = get_or_create_user(email)
    user = update_user(user.uuid, email, user.name, password)
