from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from obsync.handler.subscription import SubscriptionHandler
from obsync.handler.user import UserHandler
from obsync.handler.vault import VaultHandler
from obsync.handler.websocket import WebSocketHandler
from obsync.utils.config import ADDR_HTTP
from obsync.utils.logger import get_logger

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.route("/{path:path}", methods=["OPTIONS"])
async def options_handler(path: str) -> JSONResponse:
    return JSONResponse(content={"message": "ok"}, status_code=200)


logger = get_logger()
logger.info("Starting server...")

subscription_handler = SubscriptionHandler()
app.include_router(subscription_handler.router, prefix="/subscription")

vault_handler = VaultHandler()
app.include_router(vault_handler.router, prefix="/vault")

user_handler = UserHandler()
app.include_router(user_handler.router, prefix="/user")

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
