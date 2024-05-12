import websockets
import asyncio
import json
from websockets.legacy.server import WebSocketServerProtocol as WSCli
from .color_print import Print
from .cfg import read_server_config
from .client_classes import Channel, Client
from .data_formats import format_data, unmarshal_data

channels: dict[str, Channel] = {}

def get_channel(name: str):
    return channels[name]

def create_channel(name: str, token: str | None):
    chan = Channel(name, token)
    channels[name] = chan

def delete_channel(chan: Channel):
    del channels[chan.name]

def init_client_data(ws: WSCli):
    header = ws.request_headers
    name = header.get("ServerName")
    channel_name = header.get("ChannelName")
    token = header.get("ChannelToken")
    ipaddr = ws.remote_address
    if name is None:
        raise ValueError("Header: need server name")
    if channel_name is None:
        raise ValueError("Header: need channel name")
    if channel_name not in channels.keys():
        create_channel(channel_name, token)
    channel = get_channel(name)
    return Client(ws, name, ipaddr, channel, token)

def register_client(cli: Client):
    channel = cli.channel
    if channel.token is not None and channel.token != cli.token:
        raise ConnectionError("频道大区密码错误")

def kick_client_before_register(cli: Client, reason: str):
    asyncio.run(cli.send(format_data(None, "server.auth_failed", [reason])))

def kick_client(cli: Client, reason: str):
    asyncio.run(cli.send(format_data(None, "server.kick", [reason])))

def remove_client(cli: Client):
    chan = cli.channel
    if chan.is_member(cli):
        chan.leave(cli)

async def client_hander(ws: WSCli):
    try:
        cli = init_client_data(ws)
    except Exception as err:
        kick_client_before_register(cli, err.args[0]) # type: ignore
        return
    try:
        while 1:
            data = unmarshal_data(await ws.recv())
    except websockets.exceptions.WebSocketException as err:
        Print.print_err(f"客户端 {cli.channel.name}:{cli.name}§c 连接出现问题: {err}")
    except Exception as err:
        Print.print_err(f"客户端 {cli.channel.name}:{cli.name}§c 的数据处理出现问题: {err}")
        kick_client(cli, "服务端数据处理出现问题")
    finally:
        remove_client(cli)

def main():
    cfgs = read_server_config()
    Print.print_suc(f"服务端将在端口: §f{cfgs['开放端口']} §a开启")

    main_server = websockets.serve(client_hander, "localhost", cfgs['开放端口'])
    asyncio.get_event_loop().run_until_complete(main_server)
    asyncio.get_event_loop().run_forever()