from SuperLink import *

__extension_data__ = {
    "name": "消息互通",
    "id": "basic-msg-link",
    "version": (0, 0, 1),
    "author": "SuperScript"
}

@on_data("chat.msg")
async def on_recv_data(data: Data):
    sender: Client = data.sender # type: ignore
    chan = sender.channel
    Print.print_inf(f"玩家发言>> {chan.name} {sender.name} §7{data.content['ChatName']}: {data.content['Msg']}")
    b_data = format_data(sender, "chat.msg", {
        "Sender": sender.name,
        "ChatName": data.content['ChatName'],
        "Msg": data.content['Msg']
    })
    await chan.broadcast(b_data)