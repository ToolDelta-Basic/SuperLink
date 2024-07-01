import hashlib


class request:
    """
            请求报文数据格式 整文UTF-8
            GET/POST 1.0\r\n
            packageName: 16进制数\r\n
            sign: 关于body的签名(SHA256)\r\n
            \r\n
            body(GET不应有请求体)

            响应报文数据格式 整文UTF-8

    """

    def __init__(self, byte: bytes):
        context = byte.decode("utf-8").split("\r\n\r\n")
        foregoing = context[0].split("\r\n")
        self.head = foregoing[0].split(" ")
        self.line = {}
        self.body = None
        for i in foregoing[1:]:
            j = i.split(": ")
            self.line.pop(j[0], j[1])
        if self.head[0] == "POST":
            self.body = context[1]

    def getMethod(self) -> str:
        return self.head[0]

    def getVersion(self) -> str:
        return self.head[1]

    def getPackageName(self) -> str:
        return self.line.get("packageName")

    def getLine(self, key: str):
        return self.line.get(key)

    def getBody(self):
        return self.body


class craftRespondPackage:
    def __init__(self, code: int, body: str):
        Hash = hashlib.sha256()
        Hash.update(body)
        self.package = f"{code} 1.0\r\nsign: {Hash.hexdigest()}\r\n\r\n{body}"
        print(self.package + "sss")

    def getPackage(self):
        return self.package.encode("utf-8")
