from pony.orm import (
    Database,
    Optional,
    PrimaryKey,
    Required,
)

from obsync.utils.config import PROVIDER, VAULT_DB

db = Database()
db.bind(provider=PROVIDER, filename=VAULT_DB, create_db=True)


class VaultFile(db.Entity):
    _table_ = "vault_file"

    uid = PrimaryKey(int, auto=True)
    vault_id = Optional(str)
    hash = Optional(str)
    path = Optional(str)
    extension = Optional(str)
    size = Optional(int, size=64)
    created = Optional(int, size=64)
    modified = Optional(int, size=64)
    folder = Optional(bool)
    deleted = Optional(bool)
    data = Optional(bytes)
    newest = Required(bool, default=True)
    is_snapshot = Required(bool, default=False)


db.generate_mapping(create_tables=True)
