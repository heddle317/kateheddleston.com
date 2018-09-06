from app import bcrypt


def hash_password(password):
    if password is None:
        return None
    return bcrypt.generate_password_hash(password).decode('utf-8')


def authenticate_password(password, hash):
    if password is None or hash is None:
        return False
    return bcrypt.check_password_hash(hash, password)
