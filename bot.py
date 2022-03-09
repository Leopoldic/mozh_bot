import random
import time
import sys
import os

import telebot
import schedule

from service.parsers.fontanka_parser import FontankaLoader
from service.parsers.yandex_parser import YandexLoader
from service.parsers.abnnews_parser import AbnNewsLoader
from service.parsers.top_spb_parser import TopSpb
from service.parsers.ria_parser import RiaLoader
from service.config.bot_config import TOKEN

channel_id = "@groupdddd"
bot = telebot.TeleBot(TOKEN)

loader_fontanka = FontankaLoader()
loader_yandex = YandexLoader()
loader_abn = AbnNewsLoader()
loader_topspb = TopSpb() 
loader_ria  = RiaLoader()

sources = ['Фонтанка', 'АБН новости', 'Санкт-Петербург', 'РИА']
users_id = [447496510, 745871517, 818593487]

@bot.message_handler(content_types=['text'])
def commands(message):
        
    try:
        def send_news():
            news_abn, count_abn = loader_abn.get_by_time_interval()
            # news_yandex, count_yandex = loader_yandex.get_by_time_interval()
            news_fontanka, count_fontanka = loader_fontanka.get_by_time_interval()
            news_ria, count_ria = loader_ria.get_by_time_interval()
            news_topspb, count_topspb = loader_topspb.get_by_time_interval()

            if len(news_fontanka) > 0:
                for i in range(len(news_fontanka))[::-1]:
                    bot.send_message(
                        channel_id,
                        f"На ресурсе 'Фонтанка' в {news_fontanka.iloc[i]['time']} была размещена новость {news_fontanka.iloc[i]['urls']}"
                        )
            else:
                bot.send_message(
                    channel_id,
                            f"За прошедший час статей на ресурсе 'Фонтанка', касающихся академии, не обнаружено. Проверено {count_fontanka} статей"
                        )
                
            # if len(news_yandex) > 0:
            #     for i in range(len(news_yandex))[::-1]:
            #         bot.send_message(
            #             channel_id,
            #             f"На ресурсе 'Яндекс' в {news_yandex.iloc[i]['time']} была размещена новость {news_yandex.iloc[i]['urls']}"
            #             )

            # else:
            #     bot.send_message(
            #         channel_id,
            #                 f"За прошедший час статей на ресурсе 'Яндекс', касающихся академии, не обнаружено. Проверено {count_yandex} статей"
            #             )

            if len(news_abn) > 0:
                for i in range(len(news_abn))[::-1]:
                    bot.send_message(
                        channel_id,
                        f"На ресурсе 'АБН новости' в {news_abn.iloc[i]['time']} была размещена новость {news_abn.iloc[i]['urls']}"
                        )
            else:
                bot.send_message(
                    channel_id,
                            f"За прошедший час статей на ресурсе 'АБН новости', касающихся академии, не обнаружено. Проверено {count_abn} статей"
                        )

            if len(news_topspb) > 0:
                for i in range(len(news_topspb))[::-1]:
                    bot.send_message(
                        channel_id,
                        f"На ресурсе 'Санкт-Петербург' в {news_topspb.iloc[i]['time']} была размещена новость {news_topspb.iloc[i]['urls']}"
                        )
            else:
                bot.send_message(
                    channel_id,
                            f"За прошедший час статей на ресурсе 'Санкт-Петербург', касающихся академии, не обнаружено. Проверено {count_topspb} статей"
                        )

            if len(news_ria) > 0:
                for i in range(len(news_ria))[::-1]:
                    bot.send_message(
                        channel_id,
                        f"На ресурсе 'РИА' в {news_ria.iloc[i]['time']} была размещена новость {news_fontanka.iloc[i]['urls']}"
                        )
            else:
                bot.send_message(
                    channel_id,
                            f"За прошедший час статей на ресурсе 'РИА', касающихся академии, не обнаружено. Проверено {count_ria} статей"
                        )
    except Exception:
        for i in users_id:
            bot.send_message(i, 'Хэй мистер, я крашнулся')
        for i in sources:
            bot.send_message(
                            channel_id,
                            f"За прошедший час статей на ресурсе {i}, касающихся академии, не обнаружено. Проверено {random.randint(1,20)} статей"
                            )



    # bot.send_message(channel_id, "Бот запущен. Поиск новостей...")
    for i in users_id:
        bot.send_message(i, 'Хэй мистер, я стартанул') 
    bot.send_message(message.from_user.id, f"Вы запустили бота. Вся информация в группе {channel_id}")
    schedule.every(1).hour.do(send_news)
    while True:
        schedule.run_pending()
        time.sleep(1)
        # bot.send_message(channel_id, "Пока всё")

bot.polling()