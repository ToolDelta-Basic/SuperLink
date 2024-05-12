import os
import sys
import importlib
import traceback
from typing import Callable
from .color_print import Print
from .client_classes import Client
from .data_formats import Data

class Extensions:

    EXTENSION_DIR = "扩展功能"

    def __init__(self):
        self.on_load_cbs: list[Callable[[]]] = []
        self.on_client_join_cbs: list[Callable[[Client]]] = []
        self.on_client_leave_cbs: list[Callable[[Client]]] = []
        self.registed_data_handler: dict[str, list[Callable[[Data], bool]]] = {}

    def make_extension_folder(self):
        os.makedirs(self.EXTENSION_DIR, exist_ok=True)

    def load_extensions(self):
        if self.EXTENSION_DIR not in sys.path:
            sys.path.append(self.EXTENSION_DIR)
        try:
            for i in os.listdir(self.EXTENSION_DIR):
                importlib.import_module(i)
        except:
            Print.print_err(f"加载扩展 {i} 出现问题: \n{traceback.format_exc()}")
            raise SystemExit

    def handle_load(self):
        for func in self.on_load_cbs:
            func()

    def handle_client_join(self, cli: Client):
        for func in self.on_client_join_cbs:
            func(cli)

    def handle_client_leave(self, cli: Client):
        for func in self.on_client_leave_cbs:
            func(cli)

    def handle_data(self, data: Data):
        for func in self.registed_data_handler.get(data.type, []):
            func(data)

# Public

def on_load(f: Callable[[]]):
    """
    系统启动的时候被加载
    """
    extensions.on_load_cbs.append(f)
    return f

def on_client_join(f: Callable[[Client]]):
    """
    监听客户端连接
    """
    extensions.on_client_join_cbs.append(f)
    return f

def on_client_leave(f: Callable[[Client]]):
    """
    监听客户端断开连接
    """
    extensions.on_client_leave_cbs.append(f)
    return f

def on_data(data_type: str):
    """
    监听特定的数据类型消息
    """
    def receiver(f: Callable[[Data], bool]):
        extensions.registed_data_handler.get(data_type, [].copy()).append(f)
        return f
    return receiver

extensions = Extensions()