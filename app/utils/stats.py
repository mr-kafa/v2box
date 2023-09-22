import datetime
from dataclasses import dataclass
from v2client.enum import VMessSecurityTypes, ProxyTypes
from v2client import utils
from app.readconfig import get_config


class VMessUser:
    def __init__(
            self,
            email: str,
            inbound_tag: str = get_config()["v2rayapi"]["inbound_tag"],
            level: int = 0,
            security: VMessSecurityTypes = VMessSecurityTypes.AUTO,
            uuid: str = utils.random_uuid()
    ):
        self.inbound_tag = inbound_tag
        self.email = email
        self.level = level
        self.security = security
        self.proxyType = ProxyTypes.VMESS
        self.userUuid = uuid


@dataclass
class UsersUsage:
    email: str
    upload: float
    download: float


@dataclass
class Detail:
    flag: bool
    status: any


@dataclass
class User:
    expireDate: datetime.datetime
    traffic: int
    v2user: VMessUser
    active: bool
    protocol: str
