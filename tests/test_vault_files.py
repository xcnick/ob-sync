from uuid import uuid4
from obsync.db.vault_files_schema import (
    VaultFileModel,
    restore_file,
    insert_metadata,
    insert_data,
    get_file,
)


def test_insert_meta_data():
    id = uuid4()
    vault_id = uuid4()
    hash = "hash"
    path = "/path/to/file"
    extension = "txt"

    file_id = insert_metadata(
        vault_file=VaultFileModel(
            id=id,
            vault_id=vault_id,
            hash=hash,
            path=path,
            extension=extension,
            size=0,
            created=0,
            modified=0,
            folder=False,
            deleted=False,
            data=None,
            newest=True,
            is_snapshot=False,
        )
    )

    assert id == file_id
    file_model = get_file(id=file_id)
    assert file_model is not None
    assert file_model.id == file_id
    assert file_model.vault_id == vault_id
    assert file_model.hash == hash
    assert file_model.path == path
    assert file_model.extension == extension


def test_insert_data():
    id = uuid4()
    vault_id = uuid4()
    hash = "hash"
    path = "/path/to/file"
    extension = "txt"

    file_id = insert_metadata(
        vault_file=VaultFileModel(
            id=id,
            vault_id=vault_id,
            hash=hash,
            path=path,
            extension=extension,
            size=0,
            created=0,
            modified=0,
            folder=False,
            deleted=False,
            data=None,
            newest=True,
            is_snapshot=False,
        )
    )

    data = b"test data 1"
    insert_data(id=file_id, data=data)
    file_model = get_file(id=id)
    assert file_model is not None
    assert file_model.id == id
    assert file_model.data == data

    data = b"test data 2"
    insert_data(id=file_id, data=data)
    file_model = get_file(id=id)
    assert file_model.data == data
