import time
import sys
import os

import telebot
import schedule

from service.parsers.fontanka_parser import FontankaLoader
from service.parsers.yandex_parser import YandexLoader
from service.parsers.abnnews_parser import AbnNewsLoader
from service.config.bot_config import TOKEN

channel_id = "@groupdddd"
bot = telebot.TeleBot(TOKEN)

loader_fontanka = FontankaLoader()
loader_yandex = YandexLoader()
loader_abn = AbnNewsLoader()

@bot.message_handler(content_types=['text'])
def commands(message):
        
    def send_news():
        news_abn, count_abn = loader_abn.get_by_time_interval()
        news_yandex, count_yandex = loader_yandex.get_by_time_interval()
        news_fontanka, count_fontanka = loader_fontanka.get_by_time_interval()

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
            
        if len(news_yandex) > 0:
            for i in range(len(news_yandex))[::-1]:
                bot.send_message(
                    channel_id,
                    f"На ресурсе 'Яндекс' в {news_yandex.iloc[i]['time']} была размещена новость {news_yandex.iloc[i]['urls']}"
                    )

        else:
            bot.send_message(
                channel_id,
                        f"За прошедший час статей на ресурсе 'Яндекс', касающихся академии, не обнаружено. Проверено {count_yandex} статей"
                    )

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

    bot.send_message(channel_id, "Бот запущен. Поиск новостей...")
    bot.send_message(message.from_user.id, f"Вы запустили бота. Вся информация в группе {channel_id}")
    schedule.every(1).hour.do(send_news)
    while True:
        schedule.run_pending()
        time.sleep(1)

bot.polling()