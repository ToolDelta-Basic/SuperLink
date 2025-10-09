import asyncio
import base64
import pathlib
import ssl
import pathvalidate
import urllib.parse

import websockets
from websockets.exceptions import ConnectionClosedError, WebSocketException

from .cfg import read_server_config
from .client_classes import Channel, Client
from .color_print import Print
from .data_formats import unmarshal_data, format_sys_data
from .extensions import extensions

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
cert_file = pathlib.Path(__file__).with_name("fullchain.pem")
key_file = pathlib.Path(__file__).with_name("privkey.pem")
try:
    ssl_context.load_cert_chain(certfile=cert_file, keyfile=key_file)
    ssl_avaliable = True
except Exception:
    Print.print_war("SSL 安全证书无法使用")
    ssl_avaliable = False

channels: dict[str, Channel] = {}


def get_channel(name: str):
    return channels[name]


def create_channel(name: str, token: str | None):
    chan = Channel(name, token)
    channels[name] = chan


def delete_channel(chan: Channel):
    del channels[chan.name]


def init_client_data(ws: websockets.WebSocketServerProtocol):
    parsed_url = urllib.parse.urlparse(ws.path)
    params = urllib.parse.parse_qs(parsed_url.query)
    name = params.get("Name", [None])[0]
    channel_name = params.get("Channel", [None])[0]
    token = params.get("Token", [None])[0]
    protocol_name = params.get("Protocol", [None])[0]
    ipaddr = ws.remote_address

    if protocol_name is None:
        raise ValueError("Header: need protocol name")
    if base64.b64decode(protocol_name).decode("utf-8") != "SuperLink-v4@SuperScript":
        raise ValueError(
            f"协议名错误, 目前仅支持 SuperLink-v4@SuperScript 协议, 目前使用 {protocol_name}"
        )
    if name is None:
        raise ValueError("需要用户名")
    name = base64.b64decode(name).decode("utf-8")
    if len(name) > 15:
        raise ValueError(f"名称太长: {name[:15]}..")
    if channel_name is None:
        raise ValueError("需要大区名")
    channel_name = base64.b64decode(channel_name).decode("utf-8")
    if token:
        token = base64.b64decode(token).decode("utf-8")
    if channel_name not in channels.keys():
        try:
            pathvalidate.validate_filename(channel_name)
        except Exception:
            raise ValueError(f"{channel_name} 不能作为频道名")
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


async def kick_client_before_register(ws: websockets.WebSocketServerProtocol, reason: str):
    await ws.send(format_sys_data("server.auth_failed", {"Reason": reason}).marshal())


async def kick_client(cli: Client, reason: str):
    await cli.send(format_sys_data("server.kick", {"Reason": reason}))


async def remove_client(cli: Client):
    chan = cli.channel
    if chan.is_member(cli):
        await chan.leave(cli)


async def client_hander(ws: websockets.WebSocketServerProtocol):
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


async def main():
    Print.print_with_info("§d服服互通: 服务端 by SuperScript", "§d 加载 ")
    Print.print_with_info(
        "§d项目地址: https://github.com/ToolDelta-Basic/SuperLink", "§d 加载 "
    )
    extensions.make_extension_folder()
    extensions.load_extensions()
    cfgs = read_server_config()
    Print.print_suc(f"服务端将在端口: §f{cfgs['开放端口']} §a开启")

    await websockets.serve(client_hander, "0.0.0.0", cfgs["开放端口"])
    await extensions.handle_load()
    try:
        await asyncio.Event().wait()  # 保持事件循环运行
    except KeyboardInterrupt:
        Print.print_suc("已关闭服务端.")
        exit()
