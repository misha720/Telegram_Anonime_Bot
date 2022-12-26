'''
		Anonymous Telegram Chat 
'''

#	Import
import asyncio
import datetime
import time
import os
import sqlite3

#		AIOGRAM
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

#		Connect
import logger

class Main():
	def __init__(self):
		super(Main,self).__init__()
		
		self.token = "5825684574:AAFeFGfPREMpN2m9oxOvImqzBmMV5R-EOkM"
		self.bot = Bot(token=self.token)
		self.dp = Dispatcher(self.bot)
		logger.log(status="CREATE", text="Created USER_BOT")

		self.connect = sqlite3.connect('base.db')
		logger.log(status="CREATE", text="Created DataBase")
		self.cursor = self.connect.cursor()

		# Varaible
		self.status = "" # Статус в котором находится пользователь
		self.user_two = "" # Айди Собеседника
		self.bundle = "" # Айди связки пользователей в chats_list

	async def loop(self):

		# OnStarted
		@self.dp.message_handler(commands=["start"])
		async def command_start_handler(message: Message):

			# Загружаем индекс нашего пользователя
			self.user_one = message.from_user.id

			# Создаём 2 кнопки для быстрого управления бота
			btn_start = KeyboardButton('Начать диалог')
			btn_interest = KeyboardButton('Настроить интересы')
			main_menu = ReplyKeyboardMarkup(resize_keyboard = True).add(btn_start, btn_interest)

			await self.bot.send_message(message.from_user.id, 
				"Привет!", 
				reply_markup = main_menu)

			# Проверка на Существование Пользователя
			if not self.check_user(message.from_user.id):
				# Не существует
				self.create_new_user(message.from_user.id, str(message.from_user.username))

		# All Message
		@self.dp.message_handler(content_types="text")
		async def all_text(message: Message):

			if message.text == "Начать диалог":
				if self.research_interlocutor(message.from_user.id):

					# Нашёл собеседника
					self.status = "communication"
					await self.bot.send_message(message.from_user.id, "Собеседник найден!")

					self.cursor = self.connect.cursor()
					self.cursor.execute("INSERT INTO chats_list VALUES (null,?,?);", 
						(message.from_user.id, self.user_two))

					self.connect.commit()
					self.cursor.close()

					# Установка связки 
					self.cursor = self.connect.cursor()
					self.cursor.execute("""SELECT * FROM chats_list 
						WHERE user_one=? AND user_two=?""", (message.from_user.id,self.user_two))

					self.bundle = self.cursor.fetchone()[0]

				else:
					#Собеседнек не найден
					self.status = "search"
					await self.bot.send_message(self.user_one, "Ищу собеседника")
			
			elif message.text == "Настроить интересы":
				pass

			else:
				if self.status == "communication":
					# Если пользователь отправил сообщение другому пользователю
					
					# Сохранение запроса
					self.cursor = self.connect.cursor()
					self.cursor.execute("INSERT INTO chat VALUES (null,?,?,?,?,?);", 
						(message.from_user.id, 
							message.text,
							"None",
							self.user_two,
							self.bundle))
					# Отправка сообщения пользователю
					await self.bot.send_message(self.user_two, message.text)


		# RUN BOT
		await self.dp.start_polling(self.bot)

	def research_interlocutor(self, user_id):
		'''
			Ищет свободного собеседника

			Вернёт True, если пользователь найден
		'''
		self.cursor = self.connect.cursor()
		self.cursor.execute("SELECT * FROM user_in_search;")
		
		record = self.cursor.fetchone()

		if record is not None: # Если не пусто

			# Загружаем индекс найденного пользователя
			self.user_two = record[1]

			# Удаление записи из поиска
			self.cursor.execute("DELETE FROM user_in_search WHERE id = ?",(record[0], ))
			self.connect.commit()
			self.cursor.close()

			return True

		else:
			self.cursor.execute("INSERT INTO user_in_search VALUES (null,?);", (user_id,))
			self.connect.commit()
			self.cursor.close()

			return False

	def check_user(self, user_id):
		'''
			Проверка на существование пользователя

			Возвращает True, если пользователь зарегестрирован
		'''
		self.cursor = self.connect.cursor()
		self.cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
		if self.cursor.fetchone() is None:
			self.cursor.close()
			return False
		else:
			self.cursor.close()
			return True

	def create_new_user(self, user_id, user_name):
		'''
			Регистрирует пользователя
		'''
		logger.log(status="INSERT", text="Insert new user - " + str(user_id))
		self.cursor = self.connect.cursor()
		self.cursor.execute("INSERT INTO users VALUES(null,?,?);", (user_id,user_name))
		self.connect.commit()
		self.cursor.close()

#	Run
if __name__ == '__main__':
	engine = Main()
	asyncio.run(engine.loop())
	engine.connect.close()
