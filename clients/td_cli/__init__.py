import websockets
import json
import time
import asyncio
from dataclasses import dataclass
from typing import Any
from tooldelta import Frame, plugins, Plugin, Config, Print

# CUSTOMIZE CLASS

@dataclass
class Data:
    type: str
    content: dict

    def marshal(self) -> str:
        return json.dumps({
            "type": self.type,
            "content": self.content
        })

# PROTOCOL MAIN

def format_data(type: str, content: dict):
    return Data(type, content)

class BasicProtocol:
    # 所有服服互通协议的基类
    def __init__(self, frame: Frame, ws_ip: str, cfgs: dict):
        self.frame = frame
        self.ws_ip = ws_ip
        self.cfgs = cfgs
        self.active = False
        self.wait_reqs = {}

    def start(self):
        # 开始连接
        raise NotImplementedError

    def send(self, data: Any):
        # 发送数据
        raise NotImplementedError

    def send_and_wait_req(self, data: Any) -> Any:
        # 向服务端请求数据
        raise NotImplementedError

class SuperLinkProtocol(BasicProtocol):
    def start(self):
        asyncio.run(self.start_ws_con())

    async def start_ws_con(self):
        try:
            async with websockets.connect(
                f"ws://{self.ws_ip}",
                extra_headers={
                    "Protocol": "SuperLink-v4@SuperScript",
                    "Name": self.cfgs["此租赁服的公开显示名"],
                    "Channel": self.cfgs["登入后自动连接到的频道大区名"],
                    "Token": self.cfgs["频道密码"],
                }
            ) as ws:
                self.ws = ws
                self.active = True
                login_resp_json = json.loads(await ws.recv())
                login_resp = format_data(login_resp_json["Type"], login_resp_json["Content"])
                if login_resp.type == "server.auth_failed":
                    Print.print_err(f"服服互通: 中心服务器登录失败: {login_resp.content['Reason']}")
                elif login_resp.type == "server.auth_success":
                    Print.print_suc("服服互通: 中心服务器登录成功")
                    while 1:
                        await self.handle(json.loads(await ws.recv()))

        except websockets.exceptions.ConnectionClosedOK:
            Print.print_war(f"服服互通: 服务器断开连接")
        except Exception as err:
            Print.print_err(f"服服互通: 中心服务器连接失败: {err}")
        finally:
            self.active = False

    async def handle(self, recv_data: dict):
        data = format_data(recv_data["Type"], recv_data)
        plugins.broadcastEvt("superlink.event", data)

    async def send(self, data: Data):
        await self.ws.send(data.marshal())

    @staticmethod
    def format_data(type: str, content: dict):
        return format_data(type, content)

    async def send_and_wait_req(self, data: Data, timeout = -1):
        await self.send(data)
        req_id = data.content["UUID"]
        ptime = time.time()
        while req_id not in self.wait_reqs.keys():
            if timeout != -1 and time.time() - ptime > timeout:
                del self.wait_reqs[req_id]
                return None
        res = self.wait_reqs[req_id]
        del self.wait_reqs[req_id]
        return res


# PLUGIN MAIN


@plugins.add_plugin_as_api("服服互通")
class SuperLink(Plugin):
    name = "服服互通"
    author = "SuperScript"
    version = (0, 0, 4)

    CON_IP = "127.0.0.1:24013"

    def __init__(self, frame: Frame):
        super().__init__(frame)
        self.read_cfgs()
        self.init_funcs()

    def read_cfgs(self):
        CFG_DEFAULT = {
            "中心服务器IP": "ws://superlink.tblstudio.cn:24013",
            "服服互通协议": "SuperLink-v4@SuperScript",
            "协议附加配置": {
                "此租赁服的公开显示名": "???",
                "登入后自动连接到的频道大区名": "公共大区",
                "频道密码": ""
            }
        }
        CFG_STD = {
            "中心服务器IP": str,
            "服服互通协议": str,
            "协议附加配置": {
                "此租赁服的公开显示名": str,
                "登入后自动连接到的频道大区名": str,
                "频道密码": str
            }
        }
        self.cfg, _ = Config.getPluginConfigAndVersion(
            self.name, CFG_STD, CFG_DEFAULT, self.version
        )
        use_protocol: type[BasicProtocol] | None = {
            "SuperLink-v4@SuperScript": SuperLinkProtocol
        }.get(self.cfg["服服互通协议"])
        if use_protocol is None:
            Print.print_err(f"协议不受支持: {self.cfg['服服互通协议']}")
            raise SystemExit
        self.active_protocol = use_protocol(self.frame, self.cfg["中心服务器IP"], self.cfg["协议附加配置"])

    def init_funcs(self):
        # --------------- API -------------------
        self.send = self.active_protocol.send
        self.send_and_wait_req = self.active_protocol.send_and_wait_req
        # ---------------------------------------

    def active(self):
        self.active_protocol.start()