import json

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel, ConfigDict, Field, create_model
from uuid import UUID
from typing import Dict, Set

from obsync.handler.utils import get_jwt_email
from obsync.db.vault_schema import (
    VaultModel,
    get_vault,
    has_access_to_vault,
    set_vault_version,
)
from obsync.db.vault_files_schema import (
    delete_vault_file,
    get_deleted_files,
    get_file,
    get_file_history,
    get_vault_files,
    get_vault_size,
    insert_data,
    insert_metadata,
    restore_file,
    snapshot,
)
from obsync.utils.config import MAX_STORAGE_BYTES, secret


class ChannelManager(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    clients: Set = Field(default=set())

    def add_client(self, ws: WebSocket) -> None:
        self.clients.add(ws)

    def remove_client(self, ws: WebSocket) -> None:
        self.clients.remove(ws)

    def is_empty(self):
        return len(self.clients) == 0

    async def broadcast(self, message: Dict) -> None:
        for client in self.clients:
            await client.send_json(message)


channels = {}


def init_handler(req: str) -> (Dict, VaultModel):
    initial = json.loads(req)

    email = get_jwt_email(jwt_string=initial["token"], secret=secret)

    vault_result = get_vault(
        id=UUID(initial["id"]), keyhash=initial["keyhash"]
    )

    if has_access_to_vault(vault_id=vault_result.id, email=email):
        return initial, vault_result
    else:
        return None, None


class WebSocketHandler(object):
    async def ws_handler(self, websocket: WebSocket):
        await websocket.accept()

        err = "error"
        try:
            msg = await websocket.receive_text()
            connection_info, connected_vault = init_handler(msg)
            if connected_vault is None:
                await websocket.send_json({"error": str(err)})
                return

            await websocket.send_json({"res": "ok"})
            try:
                version = int(connection_info["version"])
            except ValueError:
                version = 0
            if connected_vault.version > version:
                vault_files = get_vault_files(connected_vault.id)
                if vault_files is None:
                    await websocket.send_json({"error": str(err)})
                    return
                for file in vault_files:
                    await websocket.send_json(
                        {
                            "op": "push",
                            "path": file.path,
                            "hash": file.hash,
                            "size": file.size,
                            "ctime": file.created,
                            "mtime": file.modified,
                            "folder": file.folder,
                            "deleted": file.deleted,
                            "device": "insignificantv5",
                            "uid": str(file.id),
                        }
                    )

            version_bumped = False
            await websocket.send_json(
                {"op": "ready", "version": connected_vault.version}
            )

            snapshot(connected_vault.id)

            if connected_vault.version < version:
                set_vault_version(connected_vault.id, version)

            if connected_vault.id not in channels:
                channels[connected_vault.id] = ChannelManager()

            channels[connected_vault.id].add_client(websocket)

            async def close_websocket():
                channels[connected_vault.id].remove_client(websocket)
                if channels[connected_vault.id].is_empty():
                    del channels[connected_vault.id]

            try:
                while True:
                    msg = await websocket.receive_text()
                    m = json.loads(msg)
                    op = m.get("op")

                    if op == "size":
                        size = get_vault_size(connected_vault.id)
                        if size == 0:
                            await websocket.send_json({"error": str(err)})
                            return
                        await websocket.send_json(
                            {
                                "res": "ok",
                                "size": size,
                                "limit": MAX_STORAGE_BYTES,
                            }
                        )

                    elif op == "pull":
                        pull_uid = m.get("uid", None)
                        if pull_uid is None:
                            await websocket.send_json(
                                {"error": "UID is required"}
                            )
                            return

                        file = get_file(UUID(pull_uid))
                        if file is None:
                            await websocket.send_json({"error": str(err)})
                            return

                        pieces = 0
                        if file.size != 0:
                            pieces = 1

                        await websocket.send_json(
                            {
                                "hash": file.hash,
                                "size": file.size,
                                "pieces": pieces,
                            }
                        )

                        if file.size != 0:
                            await websocket.send_bytes(file.data)

                    elif op == "push":
                        metadata = m
                        vault_uid = None

                        if metadata["deleted"]:
                            delete_vault_file(metadata["path"])
                            vault_uid = 0
                        else:
                            vault_meta_file = create_model(
                                "VaultMetaFileModel",
                                vault_id=(UUID, ...),
                                path=(str, ...),
                                hash=(str, ...),
                                extension=(str, ...),
                                size=(int, ...),
                                created=(int, ...),
                                modified=(int, ...),
                                folder=(bool, ...),
                                deleted=(bool, ...),
                            )

                            vault_uid = insert_metadata(
                                vault_file=vault_meta_file(
                                    vault_id=connected_vault.id,
                                    path=metadata["path"],
                                    hash=metadata["hash"],
                                    extension=metadata["extension"],
                                    size=metadata.get("size", 0),
                                    created=metadata["ctime"],
                                    modified=metadata["mtime"],
                                    folder=metadata["folder"],
                                    deleted=metadata["deleted"],
                                )
                            )

                        if vault_uid is None:
                            await websocket.send_json({"error": str(err)})
                            return

                        if metadata.get("size", 0) > 0:
                            full_binary = bytearray()
                            for _ in range(metadata["pieces"]):
                                await websocket.send_json({"res": "next"})
                                binary_message = (
                                    await websocket.receive_bytes()
                                )
                                full_binary += binary_message

                            insert_data(id=vault_uid, data=bytes(full_binary))

                        metadata["uid"] = str(vault_uid)
                        await channels[connected_vault.id].broadcast(metadata)

                        if not version_bumped:
                            set_vault_version(connected_vault.id, version + 1)
                            version_bumped = True

                        await websocket.send_json({"op": "ok"})

                    elif op == "history":
                        history = m
                        files = get_file_history(history["path"])
                        if len(files) == 0:
                            await websocket.send_json({"error": str(err)})
                            return

                        file_dumps = list(
                            map(
                                lambda f: {
                                    k: str(v) if isinstance(v, UUID) else v
                                    for k, v in f.model_dump().items()
                                    if k != "data"
                                },
                                files,
                            )
                        )
                        await websocket.send_json(
                            {
                                "items": file_dumps,
                                "more": False,
                            }
                        )

                    elif op == "ping":
                        await websocket.send_json({"op": "pong"})

                    elif op == "deleted":
                        files = get_deleted_files()
                        if len(files) == 0:
                            await websocket.send_json({"error": str(err)})
                            return
                        file_dumps = list(
                            map(
                                lambda f: {
                                    k: str(v) if isinstance(v, UUID) else v
                                    for k, v in f.model_dump().items()
                                    if k != "data"
                                },
                                files,
                            )
                        )
                        await websocket.send_json({"items": file_dumps})

                    elif op == "restore":
                        restore = m.get("uid")
                        if restore is None:
                            await websocket.send_json(
                                {"error": "UID is required"}
                            )
                            return

                        uid = UUID(restore)
                        file_res = restore_file(id=uid)

                        if file_res is None:
                            await websocket.send_json({"error": str(err)})
                            return

                        await channels[connected_vault.id].broadcast(
                            file.model_dump()
                        )
                        await websocket.send_json({"res": "ok"})

                    else:
                        print("Unknown operation:", op)
                        print("Data:", msg)

            except WebSocketDisconnect:
                await close_websocket()

        except WebSocketDisconnect:
            await close_websocket()
