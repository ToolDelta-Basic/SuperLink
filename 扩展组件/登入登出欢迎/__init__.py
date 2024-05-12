from SuperLink import *

@on_client_join
async def handler(cli: Client):
    await cli.channel.broadcast(format_data(cli, "msg.join", {"Name": cli.name}))

@on_client_leave
async def handler2(cli: Client):
    await cli.channel.broadcast(format_data(cli, "msg.leave", {"Name": cli.name}))