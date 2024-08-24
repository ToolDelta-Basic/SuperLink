from SuperLink import on_data, Data, Client, format_data

__extension_data__ = {
    "name": "查询频道在线服务器",
    "id": "check-channel-servers",
    "version": (0, 0, 1),
    "author": "SuperScript",
}


@on_data("request.channel_members")
async def handler(data: Data):
    sender: Client = data.sender
    members = [i.name for i in sender.channel.members.values()]
    await sender.send(
        format_data(
            sender, "request.resp", {"UUID": data.content["UUID"], "Data": members}
        )
    )
