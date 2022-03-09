import time

import requests
import pandas as pd
from bs4 import BeautifulSoup as bs
from datetime import datetime, timedelta
from loguru import logger
from service.parsers.core_class import MozhaikaLoader


class AbnNewsLoader(MozhaikaLoader):
    def __init__(self):
        self.main_url = 'https://abnews.ru'
        
    def get_urls(self):
        resp = requests.get(
            f'{self.main_url}/tape',
            proxies=MozhaikaLoader.get_random_proxie()
            )
        data = bs(resp.text, 'html.parser')
        
        self.urls_by_time = pd.DataFrame(columns=['urls','time'])
        self.urls_by_time['time'] = [
            str(i.text).split(" ")[-1].strip() for i in data.find_all('div', {'class':"news__foot"})
        ]

        logger.debug(self.urls_by_time['time'])
        
        self.urls_by_time['urls'] = [
            i.get('href') for i in data.find_all(
                'a', {'class':"news__item news__item--small"}
                )
        ]
        
        if len(self.urls_by_time['urls'])==0:
            logger.debug('Сработала защита от ботов')
            time.sleep(5)
            self.get_urls()

    def get_text(self,url_path):
        logger.debug(f"АБН новости проверяются: {url_path}")
        resp = requests.get(
            f'{url_path}',
            proxies=MozhaikaLoader.get_random_proxie()
            )
        data = bs(resp.text, 'html.parser')
        text_parts = data.find_all('div',{'class':'article__text'})
        header_h1 = data.find_all('p', {'class': 'news__name'})

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
            rez['urls'] = rez['urls'].apply(lambda x: f'{self.main_url}{x}')
        return rez, count_rez