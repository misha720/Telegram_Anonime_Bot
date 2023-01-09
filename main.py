'''
		Anonymous Telegram Chat 
'''

#	Import
import asyncio
import random
import datetime
import time
import os
import json

#		AIOGRAM
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

#		Connect
import logger
from db import Base

class Main():
	def __init__(self):
		super(Main,self).__init__()
		
		self.token = "5986676065:AAGLmfSyUt2Zw8lKsEmlLV46MxXowi7AFao"
		self.bot = Bot(token=self.token)
		self.dp = Dispatcher(self.bot)
		logger.log(status="CREATE", text="Created USER_BOT")

		self.connect = Base()
		logger.log(status="CREATE", text="Created DataBase")

		# Varaible
		self.status = "" # Статус в котором находится пользователь
		self.user_one = "" # Айди 1 Собеседника
		self.user_two = "" # Айди 2 Собеседника
		self.chat_id_in_list = "" # Айди чата
		self.bundle = [] # Айди активных связок пользователей в chats_list

	async def loop(self):


		# OnStarted
		@self.dp.message_handler(commands=["start"])
		async def start_command(message: Message):

			# Загружаем индекс нашего пользователя
			self.read_user(message.from_user.id)

			# Создаём 2 кнопки для быстрого управления бота
			btn_start = KeyboardButton('/search')
			btn_help = KeyboardButton('/help')
			#btn_interest = KeyboardButton('/settings')
			main_menu = ReplyKeyboardMarkup(resize_keyboard = True).add(btn_start, btn_help)

			await self.bot.send_message(message.from_user.id, 
				"Привет! Это Анонимный чат Телеграма v0.1 \nТут можно общаться 1 на 1 со случайными собеседниками.\n\nРаботает бот очень просто: вы жмете кнопку поиска или используете команду /search и бот находит вам собеседника. \nНа данный момент, Бот способен принимать: Текст, Фото и Видео. Это позволит тебе разнообразить сухое общение мемами и смешными картинками :-)\n\nУдачного общения! Будьте вежливы к собеседникам.", 
				reply_markup = main_menu)

			# Проверка на Существование Пользователя
			if not self.connect.get_user(message.from_user.id):
				# Не существует
				self.create_new_user(message.from_user.id, str(message.from_user.username))


		# OnStopedChat
		@self.dp.message_handler(commands=["stop"])
		async def stop_command(message: Message):
			
			self.read_user(message.from_user.id)

			# Вывод сообщения о отключении собеседника
			if message.from_user.id == self.user_two:
				await self.bot.send_message(self.user_one, "Собеседник закончил с вами связь")
				await self.bot.send_message(self.user_two, "Вы закончили связь с вашим собеседником")
			else:
				await self.bot.send_message(self.user_two, "Собеседник закончил с вами связь")
				await self.bot.send_message(self.user_one, "Вы закончили связь с вашим собеседником")

			# Отчистка всех переменных для общения
			self.status = "" 
			self.user_two = "" 
			for lot_index in range(len(self.bundle)):
				if self.bundle[lot_index]['user_one'] == message.from_user.id or self.bundle[lot_index]['user_two'] == message.from_user.id:
					self.bundle.pop(lot_index)

		# OnSearch
		@self.dp.message_handler(commands=["search"])
		async def search_command(message: Message):
			if self.research_interlocutor(message.from_user.id):

				# Нашёл собеседника
				self.status = "communication"

				await self.bot.send_message(message.from_user.id, 
					'Собеседник найден!\nЧто бы закончить общение, напишите "/stop"', 
					reply_markup=ReplyKeyboardRemove())

				await self.bot.send_message(self.user_two, 
					'Собеседник найден!\nЧто бы закончить общение, напишите "/stop"', 
					reply_markup=ReplyKeyboardRemove())


				self.connect.add_chats_list(self.user_one, self.user_two)
				self.connect.save()

				new_lot = {
					'user_one':message.from_user.id,
					'user_two':self.user_two,
				}
				self.bundle.append(new_lot)

			else:
				# Собеседнек не найден
				self.status = "search"
				await self.bot.send_message(message.from_user.id, 
					"Ищу собеседника",
					reply_markup=ReplyKeyboardRemove())


		# OnSettings
		@self.dp.message_handler(commands=["settings"])
		async def settings_command(message: Message):
			pass


		# OnHelp
		@self.dp.message_handler(commands=["help"])
		async def help_command(message: Message):
			await self.bot.send_message(message.from_user.id, 
				"""Анонимный чат создан только для общения между двумя пользователями. Вы не можете использовать чат чтобы привлекать пользователей на другие ресурсы, группы или чаты, продавать что-то, распространять и прочее...\n\nДа кто вообще это читает? Ты главное не беси других своими действиями. Здесь не приветствуется спам, рассылка и распространение контента, который может навредить другим.""")


		#		CHAT
		# TEXT
		@self.dp.message_handler(content_types="text")
		async def text_types(message: Message):
			self.read_user(message.from_user.id)
			if self.status == "communication":
				# Если пользователь отправил сообщение другому пользователю

				# Сохранение запроса
				self.connect.add_chat (message.from_user.id, 
						self.check_second_bundle(message.from_user.id),
						message.text,
						"None",
						self.chat_id_in_list)
				self.connect.save()

				# Отправка сообщения пользователю
				await self.bot.send_message(self.check_second_bundle(message.from_user.id), 
					message.text)


		# VIDEO
		@self.dp.message_handler(content_types=['video'])
		async def video_types(message: Message):
			self.read_user(message.from_user.id)
			if self.status == "communication":
				# Если пользователь отправил сообщение другому пользователю

				# Создание индификатора картинки
				random_path_video = "./video/video_"+str(random.randint(10000000, 99999999))+".mp4"

				# Получение файла
				file_id = message.video.file_id
				file = await self.bot.get_file(file_id)
				await self.bot.download_file(file.file_path, random_path_video)

				# Сохранение запроса
				self.connect.add_chat (message.from_user.id, 
						self.check_second_bundle(message.from_user.id),
						"*video*",
						random_path_video,
						self.chat_id_in_list)
				self.connect.save()

				# Отправка сообщения пользователю
				await self.bot.send_video(
					self.check_second_bundle(message.from_user.id), 
					open(random_path_video, 'rb'))
					

		# PHOTO
		@self.dp.message_handler(content_types=['photo'])
		async def photo_types(message: Message):
			self.read_user(message.from_user.id)
			if self.status == "communication":
				# Если пользователь отправил сообщение другому пользователю	

				# Создание индификатора картинки
				random_path_image = "./image/image_"+str(random.randint(10000000, 99999999))+".jpg"
				
				# Получение файла
				await message.photo[-1].download(
					destination_file=random_path_image)

				# Сохранение запроса
				self.connect.add_chat (message.from_user.id, 
						self.check_second_bundle(message.from_user.id),
						"*image*",
						random_path_image,
						self.chat_id_in_list)
				self.connect.save()

				# Отправка сообщения пользователю
				await self.bot.send_photo( 
					chat_id=self.check_second_bundle(message.from_user.id), 
					photo=open(random_path_image, 'rb') )
				

		# RUN BOT
		await self.dp.start_polling(self.bot)

	def read_user(self, user_id):
		'''
			Обновляет информацию о пользователе

			Заполняет ячейки - 
				user_one
				user_two
				chat_id_in_list

			Вернёт True, если пользователь находится в чате с кем то
		'''
		self.user_one = user_id

		for lot_index in range(len(self.bundle)):

			if self.bundle[lot_index]['user_one'] == user_id and self.bundle[lot_index]['user_two'] != user_id:
				self.user_two = self.bundle[lot_index]['user_two']
				self.status = "communication"
				self.chat_id_in_list = int(lot_index)
				return True

			elif self.bundle[lot_index]['user_one'] != user_id and self.bundle[lot_index]['user_two'] == user_id:
				self.user_two = self.bundle[lot_index]['user_one']
				self.status = "communication"
				self.chat_id_in_list = int(lot_index)
				return True

		# Пользователь не в чате
		self.status = ""
		return False

	def check_second_bundle(self, user_id):
		'''
			Получает индекс связки

			Вернёт True, если создателем является наш пользователь
		'''
		self.read_user(user_id)

		if user_id == self.user_one:
			return self.user_two

		else:
			return self.user_one

	def research_interlocutor(self, user_id):
		'''
			Ищет свободного собеседника

			Вернёт True, если пользователь найден
		'''
		record = self.connect.research_user_two(user_id)

		if record is not None: # Если не пусто

			# Загружаем индекс найденного пользователя
			self.user_two = record

			# Удаление записи из поиска
			self.connect.del_in_search(self.user_two)
			self.connect.save()

			return True

		else:
			self.connect.add_in_search(user_id)
			self.connect.save()

			return False

	def create_new_user(self, user_id, user_name):
		'''
			Регистрирует пользователя
		'''
		logger.log(status="INSERT", text="Insert new user - " + str(user_id))
		
		self.connect.add_new_user(user_id, user_name)
		self.connect.save()

#	Run
if __name__ == '__main__':
	engine = Main()
	asyncio.run(engine.loop())
	engine.connect.save()