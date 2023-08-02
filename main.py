"""
    SecurityChatBot v4.0
    Powered by Zero
"""

# Import
import json
import random
import asyncio
import datetime

from loguru import logger
import copy

# AioGram
from aiogram import Bot, Dispatcher
from aiogram.types import Message

# Connect
from fantome import Fantome
logger.add("debug.log",
    format="{time} {level} {message}",
    level="DEBUG")


# Main
class Main:
    def __init__(self):
        logger.debug('Initialization.')
        # Local - 5986676065:AAEhhvEE6If79a67oxtH4AgdXC3Sc6i9H14
        # Global - 6661236449:AAF2W--jWI-L075UYTSL4u02pBjB6SSkg5Y
        self.token = "6661236449:AAF2W--jWI-L075UYTSL4u02pBjB6SSkg5Y" # API token
        self.bot = Bot(token=self.token)
        self.dp = Dispatcher(self.bot)

        logger.debug('Telegram Bot connected.')

        with open("base.json", 'r') as file_base:
            self.base = json.load(file_base)
        logger.debug('Base connected.')

    async def loop(self):
        # OnStarted
        @self.dp.message_handler(commands=["start"])
        async def start_command(message: Message):

            # Проверка статуса пользователя для глушения команды
            user, user_index = self.get_user(message.from_user.id)
            if not user['status']:
                # Если не в чате
                await self.bot.send_message(message.from_user.id,
                    'Привет! Это Анонимный чат Телеграма v4.0 \nТут можно общаться 1 на 1 со случайными собеседниками.\n\nРаботает бот очень просто: вы жмете кнопку /search и бот находит вам собеседника. \nНа данный момент, Бот способен принимать: Текст, Фото, Видео и Стикеры. Это позволит тебе разнообразить общение мемами и смешными картинками :-)\n\nУдачного общения! Будьте вежливы к собеседникам.')

        # OnStopedChat
        @self.dp.message_handler(commands=["stop"])
        async def stop_command(message: Message):

            # Проверка статуса пользователя для глушения команды
            user, user_index = self.get_user(message.from_user.id)
            if user['status']:
                # Если в чате

                active_chat = {} # Чат пользователя
                # Сохранение чата
                for chat_item in self.base['bundles']:
                    if user['uid'] == chat_item['sender'] or user['uid'] == chat_item['receiver']:
                        active_chat = copy.copy(chat_item)

                        file_name = "./chats/" + str( random.randint(1000000000, 9999999999) ) + ".json"
                        with open(file_name, 'w') as file_chat:
                            json.dump(chat_item, file_chat)

                # Отправляем сообщения пользователям о заверщении диалога
                await self.bot.send_message(active_chat['sender'], "Диалог завершён")
                await self.bot.send_message(active_chat['receiver'], "Диалог завершён")

                # Открываем пользователей для поиска
                user, user_index = self.get_user(active_chat['sender'])
                self.base['users'][user_index]['status'] = False

                user, user_index = self.get_user(active_chat['receiver'])
                self.base['users'][user_index]['status'] = False

                # Удаление чата из списка
                index_bundle_delete = 0
                for chat_item in self.base['bundles']:
                    if user['uid'] == chat_item['sender'] or user['uid'] == chat_item['receiver']:
                        self.base['bundles'].pop(index_bundle_delete)
                        break
                    index_bundle_delete += 1

                self.base_update()

        # OnSearch
        @self.dp.message_handler(commands=["search"])
        async def search_command(message: Message):
            
            # Проверка статуса пользователя для глушения команды
            user, user_index = self.get_user(message.from_user.id)
            if not user['status']:
                # Если пользователь не в чате

                # Проверяем есть ли кто-то в searcher
                if len(self.base['searcher']) > 0:
                    # Если уже кто-то ищет
                    one_searcher = str(self.base['searcher'][0]) # Берём айди первого в списке

                    # Создаём новую связку
                    new_bundles = {
                        "sender":user['uid'],
                        "receiver": one_searcher,
                        "chat":[]
                    }
                    # Удаляем собеседника из очереди
                    self.base['searcher'].pop(0)

                    # Добавляем новую связку в bundles
                    self.base['bundles'].append(new_bundles) 

                    # Открываем пользователей для поиска
                    user, user_index = self.get_user(new_bundles['sender'])
                    self.base['users'][user_index]['status'] = True

                    user, user_index = self.get_user(new_bundles['receiver'])
                    self.base['users'][user_index]['status'] = True

                    # Оповещаем участников о нахождении собеседника
                    await self.bot.send_message(new_bundles['sender'],
                        'Собеседник найден!\nЕсли Вы захотите завершить диалог, напишите команду /stop')
                    await self.bot.send_message(new_bundles['receiver'],
                        'Собеседник найден!')

                    self.base_update()

                else:
                    # Если список пуст
                    await self.bot.send_message(message.from_user.id,
                        'Ищу Вам собеседника...')

                    # Добавляем пользователя в очередь
                    self.base['searcher'].append(user['uid'])
        
        
        # Text
        @self.dp.message_handler(content_types="text")
        async def text_types(message: Message):

            # Проверка статуса пользователя для глушения команды
            user, user_index = self.get_user(message.from_user.id)
            if user['status']:

                index_bundle = 0
                # Ищем связку пользователей
                for chat_item in self.base['bundles']:
                    if user['uid'] == chat_item['sender'] or user['uid'] == chat_item['receiver']:
                        bundles = chat_item
                        break
                    index_bundle += 1

                # Создаём строку в чате
                new_message = {
                    "sender" : user['uid'],
                    "receiver" : "",
                    "meassage" : str(message.text),
                    "datetime" : str( datetime.datetime.now() )
                }

                # Отправка сообщения собеседнику
                if user['uid'] == bundles['sender']:
                    new_message['receiver'] = bundles['receiver']

                    await self.bot.send_message( chat_item['receiver'], str(message.text) )

                
                else:
                    new_message['receiver'] = bundles['sender']

                    await self.bot.send_message( bundles['sender'], str(message.text) )

                logger.debug( "User - " + user['uid'] + "send to -> " + new_message['receiver'] + " | Message: " + str(message.text) )

                # Сохраняем стпроку в базе
                self.base['bundles'][index_bundle]['chat'].append(new_message)

        # Run Bot
        await self.dp.start_polling(self.bot)

    def base_update(self):
        """
            Сохранение базы данных
        """
        with open('base.json', 'w') as file_base:
            json.dump(self.base, file_base)

    def get_user(self, uid, name="", address=""):
        """
            Возвращает объект пользователя, если его нет, то создаёт
        """
        user_index = 0
        for user_item in self.base['users']:  # Перебераем каждого пользователя
            if str(uid) == user_item['uid']:
                # Если совпал ID, то возврощаем его объект
                return user_item, user_index
            user_index += 1

        # Если такого пользователя нет
        new_user = {
            "uid": str(uid),
            "name": str(name),
            "address": str(address),
            "status": False
        }
        self.base['users'].append(new_user)

        user_index = 0
        for user_item in self.base['users']:  # Перебераем каждого пользователя
            if str(uid) == user_item['uid']:

                self.base_update()

                logger.debug("New User - " + str(new_user['uid']) )
                return new_user, user_index
            user_index += 1


#   Run
if __name__ == '__main__':
    # Запускает бота
    engine = Main()
    asyncio.run(engine.loop())
