from random import choice

from service.config.bot_config import PROXIE

from loguru import logger

class ProxyLoad:
    def __init__(self, proxy):
        self.proxy = proxy
    
    def get_random_proxy(self):
        if isinstance(self.proxy, list):
            return  {'https': choice(self.proxy)}
        elif isinstance(self.proxy, str):
            return {'https': self.proxy}

n_proxies = ProxyLoad(PROXIE)