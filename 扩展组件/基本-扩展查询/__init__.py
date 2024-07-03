from SuperLink import *

__extension_data__ = {
    "name": "基本-扩展查询",
    "id": "extensions-check",
    "version": (0, 0, 1),
    "author": "System"
}

@on_data("extensions.check")
async def ext_request(data: Data):
    await data.sender.send(format_sys_data("extensions.check.resp", {"Extensions": extensions.extension_ids}))