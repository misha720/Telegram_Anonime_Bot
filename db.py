import json
import logger
import time

'''
	SCHEMA BASE:

		users{
			"user_id": INT,
			"user_name": STR
		}

		user_in_search{
			"user_id": INT
		}

		chats_list{
			"user_one": INT,
			"user_two": INT
		}

		chat{
			"user_id": INT,
			"user_recipient": INT,
			"meassage": STR,
			"file_path": STR,
			"chat_id": INT
		}
'''
class Base():
	def __init__(self):
		super(Base,self).__init__()

		with open('users.json', 'r') as base_users:
			self.users = json.load(base_users)

		with open('user_in_search.json', 'r') as base_user_in_search:
			self.user_in_search = json.load(base_user_in_search)

		with open('chats_list.json', 'r') as base_chats_list:
			self.chats_list = json.load(base_chats_list)

		with open('chat.json', 'r') as base_chat:
			self.chat = json.load(base_chat)

		with open('bundle_active.json', 'r') as base_bundle:
			self.bundle = json.load(base_bundle)

	def save(self, new_bundle):
		'''
			Сохраняет все действия с БД
		'''
		with open('users.json', 'w') as base_users:
			json.dump(self.users, base_users)

		with open('user_in_search.json', 'w') as base_user_in_search:
			json.dump(self.user_in_search, base_user_in_search)

		with open('chats_list.json', 'w') as base_chats_list:
			json.dump(self.chats_list, base_chats_list)

		with open('chat.json', 'w') as base_chat:
			json.dump(self.chat, base_chat)

		with open('bundle_active.json', 'w') as base_bundle:
			json.dump(self.bundle, base_bundle)

		logger.log(status="SAVE", text="Save DataBase")

	#	USERS
	def add_new_user(self, user_id, user_name):
		new_lot = {
			"user_id" : user_id,
			"user_name" : user_name
		}
		self.users.append(new_lot)

	def get_user(self, user_id):
		'''
			Возвращает True, если пользователь существует
		'''
		for lot in self.users:
			if lot['user_id'] == user_id:
				return True
		return False
	

	#	USER_IN_SEARCH
	def research_user_two(self, user_id):
		if len(self.user_in_search) != 0:
			if user_id != self.user_in_search[0]['user_id']:
				return self.user_in_search[0]['user_id']

	def add_in_search(self, user_id):
		# Ищем, есть ли уже такой пользователь
		for lot_index in range(len(self.user_in_search)):
			if self.user_in_search[lot_index]['user_id'] == user_id:
				# Если да, то остановить поиск и НЕ добавлять юзера
				break
		# Если нет, то добавить в очередь
		new_lot = {
			"user_id" : user_id
		}
		self.user_in_search.append(new_lot)

	def del_in_search(self, user_id):
		for lot_index in range(len(self.user_in_search)):
			if self.user_in_search[lot_index]['user_id'] == user_id:
				self.user_in_search.pop(lot_index)
				break


	#	CHATS_LIST
	def add_chats_list(self, user_one, user_two):
		new_lot = {
			"user_one" : user_one,
			"user_two" : user_two
		}
		self.chats_list.append(new_lot)


	#	CHAT
	def add_chat(self, user_id, user_recipient, text, file_path, chat_id):
		new_lot = {
			"user_id": user_id,
			"user_recipient": user_recipient,
			"meassage": text,
			"file_path": file_path,
			"chat_id": chat_id
		}
		self.chat.append(new_lot)
		logger.log(status="INSERT", text="Sand meassage:" + str(user_id) + " -> " + str(user_recipient))
