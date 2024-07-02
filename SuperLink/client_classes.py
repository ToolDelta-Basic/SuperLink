from typing import Optional, Any
from websockets.legacy.server import WebSocketServerProtocol as WSCli
from .data_formats import Data, format_data
from .utils import gather_funcs

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

    async def join(self, cli: Client):
        self.members[cli.ipaddr] = cli
        await self.broadcast(format_data(cli, "client.join", {"Name": cli.name}))

    async def leave(self, cli: Client):
        await self.broadcast(format_data(cli, "client.leave", {"Name": cli.name}))
        del self.members[cli.ipaddr]

    def is_member(self, cli: Client):
        return cli.ipaddr in self.members.keys()

    async def broadcast(self, data: Data):
        clis: list[Client] = []
        for cli in self.members.values():
            if data.sender is None or cli.ipaddr != data.sender.ipaddr:
                clis.append(cli)
        await gather_funcs(cli.send(data) for cli in clis)