from SuperLink import *

@on_data("chat.msg")
async def on_recv_data(data: Data):
    sender: Client = data.sender # type: ignore
    chan = sender.channel
    await chan.broadcast(data)