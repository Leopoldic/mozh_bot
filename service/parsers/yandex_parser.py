import re
import time
from datetime import datetime, timedelta

import asyncio
import requests
import pandas as pd
from bs4 import BeautifulSoup as bs
from aiohttp import ClientSession
from loguru import logger

from service.parsers.core_class import MozhaikaLoader
from .utils.random_user import get_chrome_random_user_agent

async def fetch(url, session):
    logger.debug(url)
    proxy = MozhaikaLoader.get_random_proxie()['https']
    async with session.get(url, proxy=proxy, headers={"User-Agent": f"{get_chrome_random_user_agent()}"}) as response:
        return await response.text()

async def run(urls):
    tasks = []
    async with ClientSession() as session:
        for i in urls:
            task = asyncio.ensure_future(fetch(i, session))
            tasks.append(task)
        responses = await asyncio.gather(*tasks)
        return responses

class YandexLoader(MozhaikaLoader):
    def __init__(self):
        self.main_url = 'https://yandex.ru'

    def get_urls(self):
        logger.debug(MozhaikaLoader.get_random_proxie())
        resp = requests.get(
            f'{self.main_url}/news',
            proxies=MozhaikaLoader.get_random_proxie(),
            headers={"User-Agent": f"{get_chrome_random_user_agent()}"}
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

    def get_text(self,resp):
        logger.debug(f"Yandex проверяется")
        resp = bs(resp)
        text_parts = resp.find_all('div',{'class':'mg-card__annotation'})
        header_h1 = resp.find_all('a', {'class': 'mg-story__title-link'})
        logger.debug(f"{' '.join([i.text for i in text_parts])}")

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
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            future = asyncio.ensure_future(run(rez['urls']))
            data = loop.run_until_complete(future)
            rez = rez[[self.check_mozhaika(i) for i in data]]
        return rez, count_rez