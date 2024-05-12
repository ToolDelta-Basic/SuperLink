import json
from websockets.legacy.server import WebSocketServerProtocol as WSCli

async def client_hander(ws: WSCli):
    print(ws.request_headers.get("a"))