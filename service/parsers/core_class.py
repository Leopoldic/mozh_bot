from abc import ABC, abstractmethod

from service.parsers.utils.proxie_load import n_proxies
from ..additional_functions.distanse import distance_hamming


class MozhaikaLoader(ABC):

    @abstractmethod
    def get_urls(self):
        raise NotImplementedError

    @abstractmethod
    def get_text(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_by_time_interval(self):
        raise NotImplementedError

    def get_random_proxie(self):
        return n_proxies.get_random_proxy()

    def check_mozhaika(self, news_url):
        news = self.get_text(news_url)
        keywords = [
                'можайка', 'можайского','а.ф.можайского', 'ф.можайского', 'военно-космичаская'
                    ]       
        for key in keywords:
            if any([distance_hamming(word.lower(), key)<3 for word in news.split()]):
                return True
        return False