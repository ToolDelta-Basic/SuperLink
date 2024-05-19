import os
import sys
import importlib
import traceback
from typing import Callable, Coroutine
from .color_print import Print
from .client_classes import Client
from .data_formats import Data
from .utils import gather_funcs

__all__ = [
    "extensions",
    "on_load",
    "on_client_join",
    "on_client_leave",
    "on_data"
]

class Extensions:

    EXTENSION_DIR = "扩展组件"
    DATA_DIR = "扩展组件数据文件"

    def __init__(self):
        self.on_load_cbs = []
        self.on_client_join_cbs = []
        self.on_client_leave_cbs = []
        self.registed_data_handler = {}

    def make_extension_folder(self):
        os.makedirs(self.EXTENSION_DIR, exist_ok=True)
        os.makedirs(self.DATA_DIR, exist_ok=True)

    def load_extensions(self):
        if self.EXTENSION_DIR not in sys.path:
            sys.path.append(self.EXTENSION_DIR)
        try:
            for i in os.listdir(self.EXTENSION_DIR):
                importlib.import_module(i)
                Print.print_suc(f"已成功加载扩展 {i}")
        except:
            Print.print_err(f"加载扩展 {i} 出现问题: \n{traceback.format_exc()}")
            raise SystemExit

    async def handle_load(self):
        await gather_funcs(func() for func in self.on_load_cbs)

    async def handle_client_join(self, cli: Client):
        await gather_funcs(func(cli) for func in self.on_client_join_cbs)

    async def handle_client_leave(self, cli: Client):
        await gather_funcs(func(cli) for func in self.on_client_leave_cbs)

    async def handle_data(self, data: Data):
        await gather_funcs(func(data) for func in self.registed_data_handler.get(data.type, ()))

# Public

def on_load(f: Callable[[], Coroutine]):
    """
    系统启动的时候被加载
    """
    extensions.on_load_cbs.append(f)
    return f

def on_client_join(f: Callable[[Client], Coroutine]):
    """
    监听客户端连接
    """
    extensions.on_client_join_cbs.append(f)
    return f

def on_client_leave(f: Callable[[Client], Coroutine]):
    """
    监听客户端断开连接
    """
    extensions.on_client_leave_cbs.append(f)
    return f

def on_data(data_type: str):
    """
    监听特定的数据类型消息
    """
    def receiver(f: Callable[[Data], Coroutine]):
        extensions.registed_data_handler.get(data_type, [].copy()).append(f)
        return f
    return receiver

extensions = Extensions()