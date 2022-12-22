'''
		Anonymous Telegram Chat 
'''

#	Import
import asyncio
import datetime
import time
import os
import sqlite3

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton


class Main():
	def __init__(self):
		super(Main,self).__init__()
		
		self.token = "5825684574:AAG7sQQqjU-SAApds6D7g5dXvSNh69tqs-o"
		self.bot = Bot(token=self.token)
		self.dp = Dispatcher(self.bot)

		self.connect = sqlite3.connect('base.db')
		self.cursor = self.connect.cursor()

	async def build(self):

		# OnStarted
		@self.dp.message_handler(commands=["start"])
		async def command_start_handler(message: Message):

			btn_start = KeyboardButton('Начать диалог')
			btn_interest = KeyboardButton('Настроить интересы')
			main_menu = ReplyKeyboardMarkup(resize_keyboard = True).add(btn_start, btn_interest)

			await self.bot.send_message(message.from_user.id, 
				"Привет!", 
				reply_markup = main_menu)

			# Проверка на Существование Пользователя
			if not self.check_user(message.from_user.id):
				# Не существует
				self.create_new_user(str(message.from_user.id), str(message.from_user.username))

		# All Message
		@self.dp.message_handler(content_types="text")
		async def all_text(message: Message):

			if message.text == "Начать диалог":
				if self.research_interlocutor(message.from_user.id):
					# Нашёл собеседника
					await self.bot.send_message(message.from_user.id, "Собеседник найден!")
				else:
					#Собеседнек не найден
					await self.bot.send_message(message.from_user.id, "Ищу собеседника")


		# RUN BOT
		await self.dp.start_polling(self.bot)

	def research_interlocutor(self, user_id):
		'''
			Ищет свободного собеседника

			Вернёт True, если пользователь найден
		'''
		self.cursor = self.connect.cursor()
		self.cursor.execute("SELECT * FROM user_in_search;")
		
		if self.cursor.fetchone() is not None: # Если не пусто
			return True
		else:
			self.cursor.execute("INSERT INTO user_in_search(user_id) VALUES (?);", (user_id,))
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
		print("Зарегестрирован новый пользователь - " + str(user_id))
		self.cursor = self.connect.cursor()
		self.cursor.execute("INSERT INTO users(user_id, fname) VALUES(?,?);", (user_id,user_name))
		self.connect.commit()
		self.cursor.close()


#	Run
if __name__ == '__main__':
	engine = Main()
	asyncio.run(engine.build())
	engine.connect.close()
