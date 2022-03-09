from re import U
import time

import requests
import pandas as pd
from bs4 import BeautifulSoup as bs
from datetime import datetime, timedelta
from loguru import logger

from service.parsers.core_class import MozhaikaLoader
from .utils.random_user import get_chrome_random_user_agent



class RiaLoader(MozhaikaLoader):
    
    def __init__(self):
        self.main_url = 'https://ria.ru'
        
    def get_urls(self):
            resp = requests.get(
                f'{self.main_url}/lenta/',
                proxies=MozhaikaLoader.get_random_proxie(),
                headers={"User-Agent": f"{get_chrome_random_user_agent()}"}
                )
            data = bs(resp.text, 'html.parser')
            self.urls_by_time = pd.DataFrame(columns=['urls','time'])
            self.urls_by_time['time'] = [
                i.text for i in data.find_all('div', 'list-item__date')
            ]        
            self.urls_by_time['urls'] = [ 
                i.get('href') for i in data.find_all("a", class_="list-item__title color-font-hover-only")
            ]

            if len(self.urls_by_time['urls'])==0:
                logger.debug('Сработала защита от ботов')
                time.sleep(5)
                self.get_urls()
            
    def get_text(self,url_path):
        logger.debug(f"Риа проверяется: {url_path}")
        resp = requests.get(
            f'{url_path}',
            proxies=MozhaikaLoader.get_random_proxie(),
            headers={"User-Agent": f"{get_chrome_random_user_agent()}"}
            )
        data = bs(resp.text, 'html.parser')
        text_parts = data.find_all('div',{'class':'article__body js-mediator-article mia-analytics'})
        header_h1 = data.find_all('div', {'class': 'article__title'})
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