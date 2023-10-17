from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from obsync.utils.logger import get_logger
from obsync.utils.config import ADDR_HTTP
from obsync.handler.vault import VaultHandler
from obsync.handler.websocket import WebSocketHandler


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = get_logger()
logger.info("Starting server...")

vault_handler = VaultHandler()
app.include_router(vault_handler.router, prefix="/vault")

websocket_handler = WebSocketHandler()
app.add_websocket_route("/", websocket_handler.ws_handler)
app.add_websocket_route("/ws", websocket_handler.ws_handler)
app.add_websocket_route("/ws.obsidian.md", websocket_handler.ws_handler)


logger.info("Serving start...")


if __name__ == "__main__":
    import uvicorn

    host = str(ADDR_HTTP.split(":")[0])
    port = int(ADDR_HTTP.split(":")[1])
    uvicorn.run(app, host=host, port=port)
