import telebot
import conf


class TelegramMessage:
    def __init__(self):
        self.bot = telebot.TeleBot(
            conf.connection_params['token'])

    def send(self, message):
        print(message)
        # self.bot.send_message(
        #     conf.connection_params['my_id'], text=message)
