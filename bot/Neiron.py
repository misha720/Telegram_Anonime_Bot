"""
	Bot for Anonim Chat Bot

	Принцип действия:
		На вход идёт сообщение пользователя. 
		Далее оно разбивается и загружается в массив.
		Первое слово сверяется со словами базы данных и записывается, получаются возможные ответы.
		Далее они фильтруются последующими словами из массива
		На выходе получается массив фраз для ответа 
"""

#	IMPORTS
import os
import json
import random

#	MAIN
class Bot():
	def __init__(self):
		super(Bot, self).__init__()
		
		# Connect DataBase
		# if os.path.isfile('database.json'):
		# 	with open('database.json', 'r',encoding='utf-8') as file_base:
		# 		self.base = json.loads(file_base)
		# else:
		# 	print("ERROR: DataBase is not faund!")
		self.base = [
			{
				"input":"привет",
				"output":"Привет, Хозяин"
			},
			{
				"input":"привет как дела",
				"output":"Привет, как у тебя дела"
			},
			{
				"input":"пока",
				"output":"Пока"
			},
			{
				"input":"пока дура",
				"output":"Пока идиот"
			},
			{
				"input":"как дела",
				"output":"Отлично, у вас как"
			},
			{
				"input":"как дела",
				"output":"Хорошо всё!"
			}
		]

	# def save_base(self):
	# 	with open('database.json','w',encoding='utf-8') as file_base:
	# 		json.dump(self.base, file_base,ensure_ascii=True)

	def random_output(self):
		len_result = len(self.crop_base)
		return str(self.crop_base[random.randint(0,len_result)]['output'])

	def filter(self, word):
		'''
			Фильтрует все фразы по слову
		'''
		second_crop = []
		
		for item_base in self.crop_base:
			list_item_input = item_base['input'].split()
			
			if word in list_item_input:
				second_crop.append(item_base)

		self.crop_base = second_crop
		# print(self.crop_base)

	def handler(self, message):
		'''
			Слово разбивается и загружается в массив
		'''
		# self.save_base()
		self.crop_base = self.base

		self.word_list = message.lower().split()
		# print(self.crop_base)

		# Filter
		for word in self.word_list:
			self.filter(word)

		# Random
		print(self.random_output())

if __name__ == '__main__':
	while True:
		engine = Bot()
		engine.handler(input(">>"))