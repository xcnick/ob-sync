from fastapi import APIRouter
#from pydantic import BaseModel
from obsync.utils.logger import get_logger


class VaultHandler(object):

    def __init__(self):
        super().__init__()
        self.router = APIRouter()
        self.router.add_route("/list", self.list, methods=["POST"])
        # self.router.add_route("/create", self.push, methods=["POST"])
        # self.router.add_route("/delete", self.pull, methods=["POST"])
        # self.router.add_route("/access", self.delete, methods=["POST"])

    async def list(
        self,
    ):
        pass
