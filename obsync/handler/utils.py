import random
import string

import jwt


def get_jwt_email(jwt_string: str, secret: bytes) -> str:
    token = jwt.decode(jwt=jwt_string, key=secret, algorithms=["HS256"])
    claims = token.get("email", None)
    return claims


def generate_password(
    length: int,
    num_digits: int,
    num_symbols: int,
    no_upper: bool,
    allow_repeat: bool,
) -> str:
    chars = string.ascii_lowercase
    if not no_upper:
        chars += string.ascii_uppercase
    if num_digits > 0:
        chars += string.digits
    if num_symbols > 0:
        chars += string.punctuation

    password = ""
    for _ in range(length):
        if not allow_repeat and len(password) > 0:
            chars = chars.replace(password[-1], "")
        password += random.choice(chars)

    return password
