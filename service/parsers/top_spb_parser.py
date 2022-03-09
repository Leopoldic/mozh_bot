import time

import requests
import pandas as pd
from bs4 import BeautifulSoup as bs
from datetime import datetime, timedelta
from loguru import logger

from service.parsers.core_class import MozhaikaLoader



class TopSpb(MozhaikaLoader):
    
    def __init__(self):
        self.main_url = 'https://topspb.tv'
        
    def get_urls(self):
            resp = requests.get(
                f'{self.main_url}/news'
                )
            data = bs(resp.text, 'html.parser')

            self.urls_by_time = pd.DataFrame(columns=['urls','time'])
            self.urls_by_time['time'] = [
                i.find("b").text.replace(",", "") for i in data.find_all('time')
            ]        
            self.urls_by_time['urls'] = [ 
                i.get('href') for i in data.find("div", class_="news-list").find_all("a", class_="news-item-media") if len(i.get('href'))
            ]
            
            if len(self.urls_by_time['urls'])==0:
                logger.debug('Сработала защита от ботов')
                time.sleep(5)
                self.get_urls()
            
    def get_text(self,url_path):
        logger.debug(f"Источник Санкт-Петербург проверяется: {self.main_url}{url_path}")
        resp = requests.get(
            f'{self.main_url}{url_path}',
            proxies=MozhaikaLoader.get_random_proxie()
            )
        data = bs(resp.text, 'html.parser')
        text_parts = data.find_all('div',{'class':'article-body'})
        header_h1 = data.find_all('h1', {'itemprop': 'name'})

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