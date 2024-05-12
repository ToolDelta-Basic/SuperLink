from typing import Optional, Any
from websockets.legacy.server import WebSocketServerProtocol as WSCli

class Client:
    def __init__(self, ws: "WSCli", name: str, ipaddr, ):
        self.ws = ws
        self.name = name
        self.ipaddr = ipaddr

class Channel:
    def __init__(self, name: str, id: str, token: Optional[str] = None):
        self.name = name
        self.id = id
        self.token = token
        self.members: dict[Any, Client] = {}

    def join(self, cli: Client):
        self.members[cli.ipaddr] = cli

    def leave(self, cli: Client):
        del self.members[cli.ipaddr]