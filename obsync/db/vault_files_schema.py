import time
from typing import Any, Dict, List, Optional

from pony.orm import commit, db_session, delete, desc, select
from pydantic import BaseModel, ConfigDict, Field

from obsync.db.vault_files import VaultFile


class VaultFileModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uid: int
    vault_id: Optional[str]
    hash: Optional[str]
    path: Optional[str]
    extension: Optional[str]
    size: Optional[int]
    created: Optional[int]
    modified: Optional[int]
    folder: Optional[bool]
    deleted: Optional[bool]
    data: Optional[bytes] = Field(exclude=True)
    newest: bool = True
    is_snapshot: bool = False


@db_session
def snapshot(vault_id: str) -> None:
    # Set newest files to be snapshots
    files = select(
        f for f in VaultFile if f.vault_id == vault_id and f.newest is True
    )
    for file in files:
        file.is_snapshot = True

    # delete all files that are not snapshots
    delete(
        f
        for f in VaultFile
        if f.vault_id == vault_id and f.is_snapshot is False
    )
    # delete all files where size is not 0 but data is null
    delete(
        f
        for f in VaultFile
        if f.size != 0 and f.data is None and f.vault_id == vault_id
    )


@db_session
def restore_file(uid: int) -> Optional[VaultFileModel]:
    vault_file = select(f for f in VaultFile if f.uid == uid).first()
    if vault_file is None:
        return None
    vault_file.uid = uid
    vault_file.deleted = False
    vault_file.newest = True
    ori_vault_file = select(
        f
        for f in VaultFile
        if f.path == vault_file.path and f.deleted is False
    )
    ori_vault_file.newest = False
    return VaultFileModel.model_validate(vault_file)


@db_session
def get_vault_size(vault_id: str) -> int:
    return select(f.size for f in VaultFile if f.vault_id == vault_id).sum()


@db_session
def get_vault_files(vault_id: str) -> List[VaultFileModel]:
    files = select(
        f
        for f in VaultFile
        if f.vault_id == vault_id and f.deleted is False and f.newest is True
    )
    return [VaultFileModel.model_validate(f) for f in files]


@db_session
def get_file(uid: int) -> Optional[VaultFileModel]:
    file = select(f for f in VaultFile if f.uid == uid).first()
    return None if file is None else VaultFileModel.model_validate(file)


@db_session
def get_file_history(path: str) -> List[VaultFileModel]:
    files = select(f for f in VaultFile if f.path == path).order_by(
        desc(VaultFile.modified)
    )
    return [VaultFileModel.model_validate(f) for f in files]


@db_session
def get_deleted_files() -> List[VaultFileModel]:
    files = select(
        f for f in VaultFile if f.deleted is True and f.newest is True
    )
    return [VaultFileModel.model_validate(f) for f in files]


@db_session
def insert_metadata(vault_file: Any) -> int:
    if vault_file.created == 0:
        vault_file.created = int(time.time()) * 1000
    if vault_file.modified == 0:
        vault_file.modified = int(time.time()) * 1000

    ori_file = select(
        f for f in VaultFile if f.path == vault_file.path and f.newest is True
    ).first()
    if ori_file is not None:
        ori_file.newest = False

    new_file = VaultFile(**vault_file.model_dump())
    commit()
    return new_file.uid


@db_session
def insert_data(uid: int, data: bytes) -> None:
    file = select(f for f in VaultFile if f.uid == uid).first()
    file.data = data


@db_session
def delete_vault_file(path: str) -> None:
    vault_files = select(f for f in VaultFile if f.path == path)
    for vault_file in vault_files:
        vault_file.deleted = True
        vault_file.is_snapshot = True
