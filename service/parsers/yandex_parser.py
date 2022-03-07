import time
from datetime import datetime, timedelta

import requests
import pandas as pd
from bs4 import BeautifulSoup as bs
from loguru import logger

from service.parsers.core_class import MozhaikaLoader



class YandexLoader(MozhaikaLoader):
    def __init__(self):
        self.main_url = 'https://yandex.ru'

    def get_urls(self):
        resp = requests.get(
            f'{self.main_url}/news',
            proxies=self.get_random_proxie()
            )
        data = bs(resp.text, 'html.parser')
        
        self.urls_by_time = pd.DataFrame(columns=['urls','time'])
        self.urls_by_time['time'] = [
            i.text for i in data.find_all('span', {'class':"mg-card-source__time"})
        ]        
        self.urls_by_time['urls'] = [
            i.get('href') for i in data.find_all('a', {'class':"mg-card__link"}) if len(i.get('href'))
        ]
        
        if len(self.urls_by_time['urls'])==0:
            logger.debug('Сработала защита от ботов')
            time.sleep(5)
            self.get_urls()

    def get_text(self,url_path):
        logger.debug(f"Yandex проверяется: {url_path}")
        resp = requests.get(
            url_path,
            proxies=self.get_random_proxie()
            )
        data = bs(resp.text, 'html.parser')
        text_parts = data.find_all('div',{'class':'mg-card__annotation'})
        header_h1 = data.find_all('a', {'class': 'mg-story__title-link'})
        

        if len(text_parts) == 0:
            logger.debug('Сработала защита от ботов')
            time.sleep(5)
            self.get_text(url_path)

        return f"{' '.join([i.text for i in header_h1])}\
                {' '.join([i.text for i in text_parts])}"

    def get_by_time_interval(self):
        self.get_urls()
        current_time = datetime.now().strftime("%H:%M")
        rez = self.urls_by_time[self.urls_by_time['time'].between(
                            (pd.to_datetime(current_time) - timedelta(hours=1)).strftime("%H:%M"),
                            current_time
                            )]
        count_rez = len(rez)
        if count_rez > 0:
            rez = rez[rez['urls'].apply(lambda x: self.check_mozhaika(x))]
        return rez, count_rez