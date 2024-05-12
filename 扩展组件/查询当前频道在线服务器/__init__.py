from SuperLink import *

@on_data("request.channel_members")
async def handler(data: Data):
    sender: Client = data.sender # type: ignore
    members = [i.name for i in sender.channel.members.values()]
    await sender.send(format_data(
        sender,
        "request.resp",
        {
            "UUID": data.content["UUID"],
            "Data": members
        }
    ))