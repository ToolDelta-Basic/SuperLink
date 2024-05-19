from SuperLink import *

__extension_data__ = {
    "name": "登入登出欢迎",
    "id": "log-welcome",
    "version": (0, 0, 1),
    "author": "SuperScript"
}

@on_client_join
async def handler(cli: Client):
    await cli.channel.broadcast(format_data(cli, "msg.join", {"Name": cli.name}))

@on_client_leave
async def handler2(cli: Client):
    await cli.channel.broadcast(format_data(cli, "msg.leave", {"Name": cli.name}))