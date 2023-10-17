import os

provider = "sqlite"

secret_filename = os.path.join(os.environ.get("DB_PATH", "."), "secret.db")
vault_filename = os.path.join(os.environ.get("DB_PATH", "."), "vault.db")
vault_files_filename = os.path.join(
    os.environ.get("DB_PATH", "."), "vault_files.db"
)

DOMAIN_NAME = os.environ.get("DOMAIN_NAME", "localhost:3000")
MAX_STORAGE_BYTES = int(os.environ.get("MAX_STORAGE_GB", 10)) * 1024 * 1024 * 1024

ADDR_HTTP = os.environ.get("ADDR_HTTP", "127.0.0.1:3000")
