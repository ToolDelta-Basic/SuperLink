from SuperLink import *

__extension_data__ = {
    "name": "消息互通",
    "id": "basic-msg-link",
    "version": (0, 0, 1)
}

@on_data("chat.msg")
async def on_recv_data(data: Data):
    sender: Client = data.sender # type: ignore
    chan = sender.channel
    await chan.broadcast(data)