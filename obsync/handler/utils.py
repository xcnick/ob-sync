import jwt
from jwt.exceptions import JWTException


def get_jwt_email(jwt_string: str) -> str:
    try:
        token = jwt.decode(jwt_string, algorithms=["HS256"])
        claims = token.get("email")
        if not claims:
            raise JWTException("invalid token")
        return claims
    except JWTException as e:
        raise e
