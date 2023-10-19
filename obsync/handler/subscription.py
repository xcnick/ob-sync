import time
from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import JSONResponse


class SubscriptionHandler(object):
    def __init__(self):
        super().__init__()
        self.router = APIRouter()
        self.router.add_route(
            "/list", self.list_subscription, methods=["POST"]
        )

    async def list_subscription(self, request: Request) -> JSONResponse:
        return JSONResponse(
            content=dict(
                business="",
                publish="",
                sync=dict(
                    earlybird=False,
                    expiry_ts=int(time.time()) * 1000
                    + (24 * 365 * 60 * 60 * 1000),
                    renew="",
                ),
            ),
            status_code=200,
        )
