import time
from typing import List, Optional
from uuid import uuid1

import bcrypt
from pony.orm import (
    db_session,
    delete,
    select,
)
from pydantic import BaseModel, ConfigDict

from obsync.db.vault import Share, User, Vault
from obsync.utils.config import DOMAIN_NAME
from obsync.utils.scrypt import make_key_hash


class VaultModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_email: str
    created: int
    host: str
    name: str
    password: str
    salt: str
    version: int
    keyhash: str


class ShareModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uid: str
    email: str
    name: str
    vault_id: str
    accepted: int


class UserModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    email: str
    password: str
    license: str


@db_session
def share_vault_invite(email: str, name: str, vault_id: str) -> ShareModel:
    share = Share(id=uuid1(), email=email, name=name, vault_id=vault_id)
    return ShareModel.model_validate(share)


@db_session
def share_vault_revoke(share_id: str, vault_id: str, email: str) -> int:
    if share_id is not None:
        return delete(
            s for s in Share if s.uid == share_id and s.vault_id == vault_id
        )
    else:
        return delete(
            s for s in Share if s.email == email and s.vault_id == vault_id
        )


@db_session
def get_vault_shares(vault_id: str) -> List[ShareModel]:
    shares = select(s for s in Share if s.vault_id == vault_id)
    return [ShareModel.model_validate(share) for share in shares]


@db_session
def get_shared_vaults(email: str) -> List[VaultModel]:
    vaults = select(
        v
        for v in Vault
        for s in Share
        if s.email == email and s.vault_id == v.id
    )
    return [VaultModel.model_validate(vault) for vault in vaults]


@db_session
def get_user_info(email: str) -> UserModel:
    user_info = select(u for u in User if u.email == email).first()
    return UserModel.model_validate(user_info)


@db_session
def is_vault_owner(vault_id: str, email: str) -> bool:
    return (
        select(
            v for v in Vault if v.id == vault_id and v.user_email == email
        ).first()
        is not None
    )


@db_session
def has_access_to_vault(vault_id: str, email: str) -> bool:
    if is_vault_owner(vault_id=vault_id, email=email):
        return True
    return (
        select(
            s for s in Share if s.vault_id == vault_id and s.email == email
        ).first()
        is not None
    )


@db_session
def new_user(name: str, email: str, password: str) -> UserModel:
    if User.exists(email=email):
        return UserModel.model_validate(User.get(email=email))
    hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    user = User(
        name=name, email=email, password=hash.decode("utf-8"), license=""
    )
    return UserModel.model_validate(user)


@db_session
def user_info(email: str) -> Optional[UserModel]:
    user_info = select(u for u in User if u.email == email).first()
    return UserModel.model_validate(user_info)


@db_session
def login(email: str, password: str) -> Optional[UserModel]:
    user_info = select(u for u in User if u.email == email).first()
    if user_info is None:
        return None
    if bcrypt.checkpw(
        password.encode("utf-8"), user_info.password.encode("utf-8")
    ):
        return UserModel.model_validate(user_info)
    return None


@db_session
def new_vault(
    name: str, user_email: str, password: str, salt: str, keyhash: str
) -> VaultModel:
    if Vault.exists(name=name, user_email=user_email):
        return VaultModel.model_validate(
            Vault.get(name=name, user_email=user_email)
        )
    if keyhash == "":
        keyhash = make_key_hash(password, salt)

    vault = Vault(
        id=str(uuid1()),
        user_email=user_email,
        created=int(time.time()) * 1000,
        host=DOMAIN_NAME,
        name=name,
        password=password,
        salt=salt,
        version=0,
        keyhash=keyhash,
    )
    return VaultModel.model_validate(vault)


@db_session
def delete_vault(id: str, email: str) -> int:
    return delete(v for v in Vault if v.id == id and v.user_email == email)


@db_session
def get_vault(id: str, keyhash: str) -> Optional[VaultModel]:
    vault = select(
        v for v in Vault if v.id == id and v.keyhash == keyhash
    ).first()
    return None if vault is None else VaultModel.model_validate(vault)


@db_session
def set_vault_version(id: str, version: int) -> None:
    vault = select(v for v in Vault if v.id == id).first()
    vault.version = version


@db_session
def get_vaults(email: str) -> Optional[List[VaultModel]]:
    vaults = select(v for v in Vault if v.user_email == email)
    return (
        None
        if vaults is None
        else [VaultModel.model_validate(vault) for vault in vaults]
    )
