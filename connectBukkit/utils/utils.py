import asyncio

from SuperLink import Channel, format_data, starter, extensions


class utils:
    @staticmethod
    def broadcastMessage(serverName, name, mess):
        cli = Channel(name)
        data = format_data(None, "chat.msg", {
            "Sender": serverName,
            "ChatName": name,
            "Msg": mess
        })
        extensions.event_loop.run_until_complete(cli.broadcast(data))
