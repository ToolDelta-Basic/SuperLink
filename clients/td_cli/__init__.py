import websockets
import json
import time
from dataclasses import dataclass
from tooldelta import Frame, plugins, Plugin, Config, Print

@dataclass
class Data:
    type: str
    content: dict

    def marshal(self) -> str:
        return json.dumps({
            "type": self.type,
            "content": self.content
        })

def format_data(type: str, content: dict):
    return Data(type, content)

class BasicProtocol:
    def __init__(self, frame: Frame, ws_ip: str, cfgs: dict):
        self.frame = frame
        self.ws_ip = ws_ip
        self.cfgs = cfgs
        self.active = False

    def start(self):
        raise NotImplementedError

class SuperLinkProtocol(BasicProtocol):
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
                    await self.start_handler()
        except websockets.exceptions.ConnectionClosedOK:
            ...
        except Exception as err:
            Print.print_err(f"服服互通: 中心服务器连接失败: {err}")
        finally:
            self.active = False
    
    async def send(self, data: Data):
        self.ws.send(data.marshal())
    
    @staticmethod
    def format_data(type: str, content: dict):
        return format_data(type, content)

    def send_and_wait_req(self, data: Data, timeout = -1):
        self.send(data)
        req_id = data.content["UUID"]
        ptime = time.time()
        while req_id not in self.wait_reqs.keys():
            if timeout != -1 and time.time() - ptime > timeout:
                del self.wait_reqs[req_id]
                return None
        res = self.wait_reqs[req_id]
        del self.wait_reqs[req_id]
        return res

@plugins.add_plugin_as_api("服服互通")
class SuperLink(Plugin):
    name = "服服互通"
    author = "SuperScript"
    version = (0, 0, 4)

    CON_IP = "127.0.0.1:24013"

    def __init__(self, frame: Frame):
        super().__init__(frame)
        self.read_cfgs()
        self.wait_reqs = {}

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
        use_protocol: dict[str, BasicProtocol] = {
            "SuperLink-v4@SuperScript": SuperLinkProtocol
        }.get(self.cfg["服服互通协议"])
        if use_protocol is None:
            Print.print_err(f"协议不受支持: {self.cfg['服服互通协议']}")
            raise SystemExit
        self.active_protocol = use_protocol(self.frame, self.cfgs["中心服务器IP"]. self.cfgs["协议附加配置"])
    
    def active(self):
        self.active_protocol.start()