import pytest
from uuid import uuid1

from obsync.db.vault_schema import (
    VaultModel,
    ShareModel,
    UserModel,
    new_user,
    login,
    new_vault,
    get_vault,
    get_vaults,
    delete_vault,
    get_user_info,
    is_vault_owner,
    has_access_to_vault,
    share_vault_invite,
    share_vault_revoke,
    get_vault_shares,
    get_shared_vaults,
)



@pytest.fixture(scope="module")
def test_user():
    new_user(
        name="Test User",
        email="test@example.com",
        password="password",
    )
    user = get_user_info(email="test@example.com")
    yield user


def test_new_vault(test_user):
    vault_name = str(uuid1())
    vault = new_vault(
        name=vault_name,
        user_email=test_user.email,
        password="password",
        salt="salt",
        keyhash="keyhash",
    )
    assert isinstance(vault, VaultModel)
    assert vault.name == vault_name
    assert vault.user_email == test_user.email


def test_get_vault(test_user):
    vault_name = str(uuid1())
    vault = new_vault(
        name=vault_name,
        user_email=test_user.email,
        password="password",
        salt="salt",
        keyhash="keyhash",
    )
    retrieved_vault = get_vault(vault.id, vault.keyhash)
    assert isinstance(retrieved_vault, VaultModel)
    assert retrieved_vault.name == vault_name
    assert retrieved_vault.user_email == test_user.email


def test_get_vaults():
    vault_name_1 = str(uuid1())
    vault_name_2 = str(uuid1())
    email = str(uuid1())
    _ = new_vault(
        name=vault_name_1,
        user_email=email,
        password="password",
        salt="salt",
        keyhash="keyhash",
    )
    _ = new_vault(
        name=vault_name_2,
        user_email=email,
        password="password",
        salt="salt",
        keyhash="keyhash",
    )
    vaults = get_vaults(email)
    assert len(vaults) == 2
    assert vaults[0].name == vault_name_1
    assert vaults[1].name == vault_name_2


def test_delete_vault(test_user):
    vault_name = str(uuid1())
    vault = new_vault(
        name=vault_name,
        user_email=test_user.email,
        password="password",
        salt="salt",
        keyhash="keyhash",
    )
    delete_vault(vault.id, test_user.email)
    assert get_vault(vault.id, vault.keyhash) is None


def test_is_vault_owner(test_user):
    vault_name = str(uuid1())
    vault = new_vault(
        name=vault_name,
        user_email=test_user.email,
        password="password",
        salt="salt",
        keyhash="keyhash",
    )
    assert is_vault_owner(vault.id, test_user.email)


def test_has_access_to_vault(test_user):
    vault_name = str(uuid1())
    vault = new_vault(
        name=vault_name,
        user_email=test_user.email,
        password="password",
        salt="salt",
        keyhash="keyhash",
    )
    assert has_access_to_vault(vault.id, test_user.email)


def test_share_vault_invite(test_user):
    vault_name = str(uuid1())
    vault = new_vault(
        name=vault_name,
        user_email=test_user.email,
        password="password",
        salt="salt",
        keyhash="keyhash",
    )
    email = str(uuid1())
    share_vault_invite(
        email=email,
        name="Test User 2",
        vault_id=vault.id,
    )
    shares = get_vault_shares(vault.id)
    assert len(shares) == 1
    assert shares[0].email == email


def test_share_vault_revoke(test_user):
    vault_name = str(uuid1())
    vault = new_vault(
        name=vault_name,
        user_email=test_user.email,
        password="password",
        salt="salt",
        keyhash="keyhash",
    )
    email = str(uuid1())
    share_vault_invite(
        email=email,
        name="Test User 3",
        vault_id=vault.id,
    )
    share = get_vault_shares(vault.id)[0]
    share_vault_revoke(
        share_id=share.id,
        vault_id=vault.id,
        email="",
    )
    assert len(get_vault_shares(vault.id)) == 0


def test_get_shared_vaults():
    vault_name_1 = str(uuid1())
    vault_name_2 = str(uuid1())
    email = str(uuid1())
    vault1 = new_vault(
        name=vault_name_1,
        user_email=email,
        password="password",
        salt="salt",
        keyhash="keyhash",
    )
    invite_email = str(uuid1())
    share_vault_invite(
        email=invite_email,
        name="Test User",
        vault_id=vault1.id,
    )
    _ = new_vault(
        name=vault_name_2,
        user_email=email,
        password="password",
        salt="salt",
        keyhash="keyhash",
    )
    shared_vaults = get_shared_vaults(invite_email)
    assert len(shared_vaults) == 1
    assert shared_vaults[0].name == vault_name_1
