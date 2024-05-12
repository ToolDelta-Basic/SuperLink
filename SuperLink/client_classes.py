from typing import Optional, Any
from websockets.legacy.server import WebSocketServerProtocol as WSCli
from .data_formats import Data

class Client:
    def __init__(self, ws: "WSCli", name: str, ipaddr, channel: "Channel", token: str | None):
        self.ws = ws
        self.name = name
        self.ipaddr = ipaddr
        self.channel = channel
        self.token = token

    async def send(self, data: Data):
        await self.ws.send(data.marshal())

class Channel:
    def __init__(self, name: str, token: Optional[str] = None):
        self.name = name
        self.token = token
        self.members: dict[Any, Client] = {}

    def join(self, cli: Client):
        self.members[cli.ipaddr] = cli

    def leave(self, cli: Client):
        del self.members[cli.ipaddr]

    def is_member(self, cli: Client):
        return cli.ipaddr in self.members.keys()