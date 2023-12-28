from typing import List, Optional

from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from obsync.db.vault_schema import (
    VaultModel,
    delete_vault,
    get_shared_vaults,
    get_vault,
    get_vaults,
    has_access_to_vault,
    new_vault,
    user_info,
)
from obsync.handler.utils import generate_password, get_jwt_email
from obsync.utils.config import secret
from pydantic import BaseModel, ConfigDict, ValidationError


class VaultHandler(object):
    def __init__(self) -> None:
        super().__init__()
        self.router = APIRouter()
        self.router.add_route("/list", self.list_vault, methods=["POST"])
        self.router.add_route("/create", self.create_vault, methods=["POST"])
        self.router.add_route("/delete", self.delete_vault, methods=["POST"])
        self.router.add_route("/access", self.access_vault, methods=["POST"])

    async def list_vault(self, request: Request) -> JSONResponse:
        class Req(BaseModel):
            model_config = ConfigDict(from_attributes=True)

            token: str

        class Res(BaseModel):
            model_config = ConfigDict(from_attributes=True)

            shared: List[VaultModel]
            vaults: List[VaultModel]
            limit: int

        req_json = await request.json()
        try:
            req = Req.model_validate(req_json)
        except ValidationError as e:
            return JSONResponse(content=e, status_code=400)

        email = get_jwt_email(jwt_string=req.token, secret=secret)
        if email is None:
            return JSONResponse(content="Invalid token", status_code=401)

        vaults = get_vaults(email=email)
        if vaults is None:
            return JSONResponse(content="Invalid email", status_code=500)

        shared = get_shared_vaults(email=email)
        if shared is None:
            return JSONResponse(content="Invalid email", status_code=500)

        return JSONResponse(
            content=Res(
                shared=shared,
                vaults=vaults,
                limit=100,
            ).model_dump(),
            status_code=200,
        )

    async def create_vault(self, request: Request) -> JSONResponse:
        class Req(BaseModel):
            model_config = ConfigDict(from_attributes=True)

            keyhash: Optional[str] = ""
            name: str
            salt: Optional[str] = ""
            token: str

        req_json = await request.json()
        try:
            req = Req.model_validate(req_json)
        except ValidationError as e:
            return JSONResponse(content=e, status_code=400)

        email = get_jwt_email(jwt_string=req.token, secret=secret)
        if email is None:
            return JSONResponse(content="Invalid token", status_code=401)

        password = ""
        salt = ""
        keyhash = ""
        if req.salt == "":
            password = generate_password(
                length=20,
                num_digits=5,
                num_symbols=5,
                no_upper=False,
                allow_repeat=True,
            )
            salt = generate_password(
                length=20,
                num_digits=5,
                num_symbols=5,
                no_upper=False,
                allow_repeat=True,
            )
        else:
            salt = req.salt
            if req.keyhash != "":
                keyhash = req.keyhash
            else:
                return JSONResponse(
                    content="keyhash must be provided if salt is provided",
                    status_code=400,
                )

        vault = new_vault(
            name=req.name,
            user_email=email,
            password=password,
            salt=salt,
            keyhash=keyhash,
        )
        if vault is None:
            return JSONResponse(content="Invalid vault", status_code=500)

        return JSONResponse(
            content=vault.model_dump(),
            status_code=200,
        )

    async def delete_vault(self, request: Request) -> JSONResponse:
        class Req(BaseModel):
            model_config = ConfigDict(from_attributes=True)

            token: str
            vault_uid: str

        req_json = await request.json()
        try:
            req = Req.model_validate(req_json)
        except ValidationError as e:
            return JSONResponse(content=e, status_code=400)

        email = get_jwt_email(jwt_string=req.token, secret=secret)
        if email is None:
            return JSONResponse(content="Invalid token", status_code=401)

        vault_deleted = delete_vault(id=req.vault_uid, email=email)
        if vault_deleted > 0:
            return JSONResponse(content={}, status_code=200)
        else:
            return JSONResponse(content="Delete vault error", status_code=500)

    async def access_vault(self, request: Request) -> JSONResponse:
        class Req(BaseModel):
            model_config = ConfigDict(from_attributes=True)

            host: str
            keyhash: str
            token: str
            vault_uid: str

        class Res(BaseModel):
            model_config = ConfigDict(from_attributes=True)

            allowed: bool = True
            email: str
            name: str

        req_json = await request.json()
        try:
            req = Req.model_validate(req_json)
        except ValidationError as e:
            return JSONResponse(content=e, status_code=400)

        email = get_jwt_email(jwt_string=req.token, secret=secret)
        if email is None:
            return JSONResponse(content="Invalid token", status_code=401)

        if not has_access_to_vault(vault_id=req.vault_uid, email=email):
            return JSONResponse(
                content="You do not have access to this vault", status_code=401
            )

        vault = get_vault(id=req.vault_uid, keyhash=req.keyhash)
        if vault is None:
            return JSONResponse(content="Error vault", status_code=500)

        user = user_info(email=email)
        if user is None:
            return JSONResponse(content="Error user info", status_code=500)

        return JSONResponse(
            content=Res(
                email=email,
                name=user.name,
            ).model_dump_json(),
            status_code=200,
        )
