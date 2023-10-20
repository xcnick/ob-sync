from uuid import UUID

from pony.orm import (
    Database,
    Optional,
    PrimaryKey,
    Required,
)

from obsync.utils.config import PROVIDER, VAULT_DB

db = Database()
db.bind(provider=PROVIDER, filename=VAULT_DB, create_db=True)


class Vault(db.Entity):
    _table_ = "vault"

    id = PrimaryKey(UUID, auto=True)
    user_email = Required(str)
    created = Required(int, size=64)
    host = Required(str)
    name = Required(str)
    password = Required(str)
    salt = Required(str)
    version = Required(int, default=0)
    keyhash = Required(str)


class Share(db.Entity):
    _table_ = "share"

    id = PrimaryKey(UUID, auto=True)
    email = Required(str)
    name = Required(str)
    vault_id = Required(UUID)
    accepted = Required(bool, default=True)


class User(db.Entity):
    _table_ = "user"

    name = Required(str)
    email = PrimaryKey(str)
    password = Required(str)
    license = Optional(str)


db.generate_mapping(create_tables=True)
