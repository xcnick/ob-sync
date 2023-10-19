import time
from uuid import UUID
from typing import List, Optional
from pony.orm import db_session, delete, select, desc
from pydantic import BaseModel, ConfigDict

from obsync.db.vault_files import VaultFile


class VaultFileModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    vault_id: Optional[UUID]
    hash: Optional[str]
    path: Optional[str]
    extension: Optional[str]
    size: Optional[int]
    created: Optional[int]
    modified: Optional[int]
    folder: Optional[bool]
    deleted: Optional[bool]
    data: Optional[bytes]
    newest: bool
    is_snapshot: bool


class FileRepsonse(BaseModel):
    vault_file: VaultFileModel
    op: str


@db_session
def snapshot(vault_id: UUID) -> None:
    # Set newest files to be snapshots
    files = select(
        f for f in VaultFile if f.vault_id == vault_id and f.newest == True
    )
    for file in files:
        file.is_snapshot = True
    # delete all files that are not snapshots
    delete(
        f
        for f in VaultFile
        if f.vault_id == vault_id and f.is_snapshot == False
    )
    # delete all files where size is not 0 but data is null
    delete(
        f
        for f in VaultFile
        if f.size != 0 and f.data == None and f.vault_id == vault_id
    )


@db_session
def restore_file(id: UUID) -> Optional[FileRepsonse]:
    vault_file = select(f for f in VaultFile if f.id == id).first()
    if vault_file is None:
        return None
    vault_file.deleted = False
    vault_file.newest = True
    ori_vault_file = select(
        f
        for f in VaultFile
        if f.path == vault_file.path and f.deleted == False
    )
    ori_vault_file.newest = False
    return FileRepsonse(vault_file=vault_file, op="push")


@db_session
def get_vault_size(vault_id: UUID) -> int:
    return select(f.size for f in VaultFile if f.vault_id == vault_id).sum()


@db_session
def get_vault_files(vault_id: UUID) -> List[VaultFileModel]:
    files = select(
        f
        for f in VaultFile
        if f.vault_id == vault_id and f.deleted == False and f.newest == True
    )
    return [VaultFileModel.model_validate(f) for f in files]


@db_session
def get_file(id: UUID) -> VaultFileModel:
    file = select(f for f in VaultFile if f.id == id).first()
    return VaultFileModel.model_validate(file)


@db_session
def get_file_history(path: str) -> List[VaultFileModel]:
    files = select(f for f in VaultFile if f.path == path).order_by(
        desc(VaultFile.modified)
    )
    return [VaultFileModel.model_validate(f) for f in files]


@db_session
def get_deleted_files() -> List[VaultFileModel]:
    files = select(
        f for f in VaultFile if f.deleted == True and f.newest == True
    )
    return [VaultFileModel.model_validate(f) for f in files]


@db_session
def insert_metadata(vault_file: VaultFileModel) -> UUID:
    if vault_file.created == 0:
        vault_file.created = int(time.time()) * 1000
    if vault_file.modified == 0:
        vault_file.modified = int(time.time()) * 1000

    ori_file = select(f for f in VaultFile if f.path == vault_file.path)
    ori_file.newest = False

    new_file = VaultFile(**vault_file.model_dump())
    return new_file.id


@db_session
def insert_data(id: UUID, data: bytes) -> None:
    file = select(f for f in VaultFile if f.id == id).first()
    file.data = data


@db_session
def delete_vault_file(path: str) -> None:
    vault_file = select(f for f in VaultFile if f.path == path)
    vault_file.deleted = True
    vault_file.is_snapshot = True
