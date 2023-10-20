import os
import pickle

PROVIDER = "sqlite"

VAULT_DB = os.path.join(os.environ.get("DB_PATH", "."), "vaults.db")

DOMAIN_NAME = os.environ.get("DOMAIN_NAME", "localhost:3000")
MAX_STORAGE_BYTES = (
    int(os.environ.get("MAX_STORAGE_GB", 10)) * 1024 * 1024 * 1024
)

ADDR_HTTP = os.environ.get("ADDR_HTTP", "127.0.0.1:3000")
SECRET_PATH = os.path.join(os.environ.get("DB_PATH", "."), "secret.gob")


def get_secret(secret_path: str) -> bytes:
    if not os.path.exists(secret_path):
        os.makedirs(os.path.dirname(secret_path), exist_ok=True)
        secret = os.urandom(64)
        with open(secret_path, "wb") as f:
            pickle.dump(secret, f)
    else:
        with open(secret_path, "rb") as f:
            secret = pickle.load(f)
    return secret


secret = get_secret(SECRET_PATH)
