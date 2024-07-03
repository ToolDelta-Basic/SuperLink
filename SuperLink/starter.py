import asyncio
import base64
import json
import pathlib
import ssl

import websockets
from websockets.exceptions import ConnectionClosedError, WebSocketException
from websockets.legacy.server import WebSocketServerProtocol as WSCli

from .cfg import read_server_config
from .client_classes import Channel, Client
from .color_print import Print
from .data_formats import format_data, unmarshal_data, format_sys_data
from .extensions import extensions

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
cert_file = pathlib.Path(__file__).with_name("fullchain.pem")
key_file = pathlib.Path(__file__).with_name("privkey.pem")
ssl_context.load_cert_chain(certfile=cert_file, keyfile=key_file)

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
    html_ws_reqs = header.get("Sec-WebSocket-Protocol")
    if html_ws_reqs:
        try:
            header = json.loads(html_ws_reqs)
        except json.JSONDecodeError:
            raise ValueError("Header: Sec-WS-Proto is not a valid json object")
    name = header.get("ServerName")
    channel_name = header.get("ChannelName")
    token = header.get("ChannelToken")
    protocol_name = header.get("Protocol")
    ipaddr = ws.remote_address
    if protocol_name != "SuperLink-v4@SuperScript":
        raise ValueError(
            f"协议名错误, 目前仅支持 SuperLink-v4@SuperScript 协议, 目前使用 {protocol_name}"
        )
    if name is None:
        raise ValueError("Header: need server name")
    if channel_name is None:
        raise ValueError("Header: need channel name")
    name = base64.b64decode(name).decode("utf-8")
    channel_name = base64.b64decode(channel_name).decode("utf-8")
    if token:
        token = base64.b64decode(token).decode("utf-8")
    if channel_name not in channels.keys():
        create_channel(channel_name, token)
    else:
        if channels[channel_name].token and channels[channel_name].token != token:
            raise ValueError("频道密码错误")
    channel = get_channel(channel_name)
    Print.print_inf(f"客户端 {ipaddr[0]}:{ipaddr[1]} 已作为 {channel.name}>{name} 登录")
    return Client(ws, name, ipaddr, channel, token)


def register_client(cli: Client):
    channel = cli.channel
    if channel.token is not None and channel.token != cli.token:
        raise ConnectionError("频道大区密码错误")


async def kick_client_before_register(ws: WSCli, reason: str):
    await ws.send(format_sys_data("server.auth_failed", {"Reason": reason}).marshal())


async def kick_client(cli: Client, reason: str):
    await cli.send(format_sys_data("server.kick", {"Reason": reason}))


async def remove_client(cli: Client):
    chan = cli.channel
    if chan.is_member(cli):
        await chan.leave(cli)


async def client_hander(ws: WSCli):
    try:
        cli = init_client_data(ws)
        await cli.channel.join(cli)
    except Exception as err:
        Print.print_err(
            f"客户端 {ws.remote_address[0]}:{ws.remote_address[1]}§c 登录出现问题: {err}"
        )
        await kick_client_before_register(ws, err.args[0])
        return
    try:
        await ws.send(
            format_sys_data(
                "server.auth_success", {"Member_count": len(cli.channel.members)}
            ).marshal()
        )
        await extensions.handle_client_join(cli)
        while 1:
            data = unmarshal_data(await ws.recv(), cli)
            await extensions.handle_data(data)
    except ConnectionClosedError:
        Print.print_inf(f"客户端 {cli.channel.name}:{cli.name}§c 断开连接")
    except WebSocketException as err:
        Print.print_err(f"客户端 {cli.channel.name}:{cli.name}§c 连接出现问题: {err}")
    except Exception as err:
        import traceback

        traceback.print_exc()
        Print.print_err(
            f"客户端 {cli.channel.name}:{cli.name}§c 的数据处理出现问题: {err}"
        )
        await kick_client(cli, "服务端数据处理出现问题")
    finally:
        try:
            await extensions.handle_client_leave(cli)
        finally:
            await remove_client(cli)


def main():
    Print.print_with_info("§d服服互通: 服务端 by SuperScript", "§d 加载 ")
    Print.print_with_info(
        "§d项目地址: https://github.com/ToolDelta/SuperLink", "§d 加载 "
    )
    extensions.make_extension_folder()
    extensions.load_extensions()
    cfgs = read_server_config()
    Print.print_suc(f"服务端将在端口: §f{cfgs['开放端口']} §a开启")

    global_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(global_loop)
    extensions.set_event_loop(global_loop)

    main_server = websockets.serve(client_hander, "0.0.0.0", cfgs["开放端口"])  # type: ignore
    global_loop.run_until_complete(main_server)
    asyncio.run(extensions.handle_load())
    try:
        global_loop.run_forever()
    except KeyboardInterrupt:
        Print.print_suc("已关闭服务端.")
        exit()
