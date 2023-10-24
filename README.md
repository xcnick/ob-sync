# ObSync

> [!NOTE]
> This is the Python implementation of [obi-sync](https://github.com/acheong08/obi-sync).
> It only supports Obsidian versions 1.4.5 and earlier.

## Running Instructions

To run the service directly, you need to install the necessary dependencies.

```bash
# Start the service
DB_PATH=/your_db_files_dir python start_server.py
# Or
DB_PATH=/your_db_files_dir uvicorn start_server:app --host 0.0.0.0 --port 3000
```

Running the service using a container

```bash
# Build the Docker image
docker build -t ob-sync -f dockerfile .

# Start the container
docker compose up -d
```

User Registration

```bash
DB_PATH=/your_db_files_dir python sign_up.py -n name -e example@email.com -p password
# Or
docker exec -it -e DB_PATH=/workspace/your_db_files_dir ob-sync python sign_up.py -n name -e example@email.com -p password
```

After deploying the server, install and configure the plugin from https://github.com/acheong08/rev-obsidian-sync-plugin in the Obsidian client.

## Acknowledgments

- [acheong08/obi-sync](https://github.com/acheong08/obi-sync)
