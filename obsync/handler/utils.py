import jwt
from jwt.exceptions import InvalidSignatureError


def get_jwt_email(jwt_string: str, secret: bytes) -> str:
    try:
        token = jwt.decode(jwt=jwt_string, key=secret, algorithms=["HS256"])
        claims = token.get("email")
        if not claims:
            raise InvalidSignatureError("invalid token")
        return claims
    except InvalidSignatureError as e:
        raise e
