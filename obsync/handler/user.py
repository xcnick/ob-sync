import time
from uuid import uuid1

import jwt
from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, ValidationError

from obsync.db.vault_schema import login, new_user, user_info
from obsync.handler.utils import get_jwt_email
from obsync.utils.config import SIGNUP_KEY, secret


class UserHandler(object):
    def __init__(self) -> None:
        super().__init__()
        self.router = APIRouter()
        self.router.add_route("/signin", self.sign_in, methods=["POST"])
        self.router.add_route("/signup", self.sign_up, methods=["POST"])
        self.router.add_route("/signout", self.sign_out, methods=["POST"])
        self.router.add_route("/info", self.user_info, methods=["POST"])

    async def sign_in(self, request: Request) -> JSONResponse:
        class Req(BaseModel):
            model_config = ConfigDict(from_attributes=True)

            email: str
            password: str

        class Res(BaseModel):
            model_config = ConfigDict(from_attributes=True)

            email: str
            license: str
            name: str
            token: str

        req_json = await request.json()
        try:
            req = Req.model_validate(req_json)
        except ValidationError as e:
            return JSONResponse(content={"error": e}, status_code=400)

        user_info = login(email=req.email, password=req.password)
        if user_info is None:
            print("Invalid password")
            return JSONResponse(
                content={"error": "Invalid password or email"},
                status_code=200,
            )

        payload = {"email": user_info.email}
        token = jwt.encode(payload, secret, algorithm="HS256")
        return JSONResponse(
            content=Res(
                email=user_info.email,
                license=user_info.license,
                name=user_info.name,
                token=token,
            ).model_dump(),
            status_code=200,
        )

    async def user_info(self, request: Request) -> JSONResponse:
        class Req(BaseModel):
            model_config = ConfigDict(from_attributes=True)

            token: str

        class Res(BaseModel):
            class status(BaseModel):
                model_config = ConfigDict(from_attributes=True)
                status: str = "approved"
                expiry_ts: int = int(time.time()) * 1000 + (
                    24 * 365 * 60 * 60 * 1000
                )
                type: str = "education"

            model_config = ConfigDict(from_attributes=True)

            uid: str
            email: str
            name: str
            payment: str = ""
            license: str = ""
            credit: int = 0
            mfa: bool = False
            discount: status = status()

        req_json = await request.json()
        try:
            req = Req.model_validate(req_json)
        except ValidationError as e:
            return JSONResponse(content={"error": e}, status_code=400)
        email = get_jwt_email(jwt_string=req.token, secret=secret)
        if email is None:
            return JSONResponse(
                content={"error": "not logged in"}, status_code=200
            )
        user = user_info(email=email)
        if user is None:
            return JSONResponse(
                content={"error": "not logged in"}, status_code=200
            )

        return JSONResponse(
            content=Res(
                uid=str(uuid1()),
                email=email,
                name=user.name,
            ).model_dump(),
            status_code=200,
        )

    async def sign_up(self, request: Request) -> JSONResponse:
        class Req(BaseModel):
            model_config = ConfigDict(from_attributes=True)

            email: str
            password: str
            fullname: str
            signup_key: str

        class Res(BaseModel):
            model_config = ConfigDict(from_attributes=True)

            email: str
            name: str

        req_json = await request.json()
        try:
            req = Req.model_validate(req_json)
        except ValidationError as e:
            return JSONResponse(content=e, status_code=400)

        if SIGNUP_KEY is not None and req.signup_key != SIGNUP_KEY:
            return JSONResponse(
                content={"error": "Invalid signup key"}, status_code=400
            )

        user_model = new_user(
            name=req.fullname, email=req.email, password=req.password.strip()
        )
        if user_model is None:
            return JSONResponse(
                content={"error": "not sign up"}, status_code=500
            )

        return JSONResponse(
            content=Res(
                email=req.email,
                name=req.fullname,
            ).model_dump(),
            status_code=200,
        )

    async def sign_out(self, _: Request) -> JSONResponse:
        return JSONResponse(content={}, status_code=200)
