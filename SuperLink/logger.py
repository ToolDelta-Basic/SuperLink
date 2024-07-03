"日志记录器"

import os
import time


class Logger:
    "ToolDelta的日志记录器"

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"
    OTHER_TYPE = "???"

    def __init__(self, log_path, name_fmt="%Y-%m-%d"):
        "初始化"
        self.path = log_path
        self.name_fmt = name_fmt
        self.now_day = time.strftime("%Y-%m-%d")
        self.logging_fmt = "[%H-%M-%S]"
        self.lastLogTime = time.time()
        self.open_wrapper_io(log_path)
        self.enable_logger = False
        self.writable = True

    def switch_logger(self, isopen: bool) -> None:
        "切换日志记录器状态"
        self.enable_logger = isopen

    def open_wrapper_io(self, log_path: str) -> None:
        "打开IO流"
        self._wrapper = open(
            log_path + os.sep + time.strftime(self.name_fmt) + ".log",
            "a",
            encoding="utf-8",
            buffering=4096,
        )

    def log_in(self, msg, level=INFO) -> None:
        "写入日志信息. level给定了其等级."
        if not self.writable or not self.enable_logger:
            return
        if not isinstance(msg, str):
            raise TypeError("only allows string")
        if "\n" in msg:
            msg = msg.replace("\n", "\n    ")
        if len(msg) > 200:
            msg = msg[:200] + "..."
        self._check_is_another_day()
        self._wrapper.write(
            time.strftime(self.logging_fmt)
            + f" [{level}] "
            + (msg if msg.endswith("\n") else msg + "\n")
        )
        if time.time() - self.lastLogTime > 15:
            self._save_log()
            self.lastLogTime = time.time()

    def _save_log(self) -> None:
        "保存日志"
        self._wrapper.flush()

    def _check_is_another_day(self) -> None:
        "判断记录日志的时候是否已经是第二天, 是的话就变更文件名"
        if time.strftime("%Y-%m-%d") != self.now_day:
            self.exit()
            self.open_wrapper_io(self.path)

    def exit(self) -> None:
        "退出时调用"
        if self.writable:
            self.writable = False
            self._save_log()
            self._wrapper.close()


def new_logger(log_path: str) -> Logger:
    "创建一个新的日志记录器"
    os.makedirs(log_path, exist_ok=True)
    return Logger(log_path)


publicLogger = new_logger("服务端日志")
