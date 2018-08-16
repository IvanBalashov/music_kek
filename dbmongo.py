from pymongo import MongoClient, ConnectionFailure

class DBProvider(object):
# files - {'file_name': f_name,
#           'downloaded_url': d_url,
#           'files': [f1,f2,f3], // if this is big file
#         } 
# users - {'user_name':u_name,
#          'u_id': u_id,
#          'files': [files] // think about this field, dk rly this need or not
#         }

	def __init__(self, my_host, port, data_base):
		try:
			self.client = MongoClient(my_host, port)
		except ConnectionFailure:
			raise Exception(f"client can't connect to mongodb.")
		self.db = self.client[data_base]
		self.files = self.db.files
		self.users = self.db.users
			
	def insert_file_in_db(self, data):
		#poka tak, na praktike posmotrim chto da kak.
		if data is None:
			raise Exception(f"empty data for save.")
		else:
			file_id = self.files.insert_one(data).inserted_id
			print(f"insert_file_in_db - {file_id}")

	def insert_user_in_db(self, data):
		if data is None:
			raise Exception(f"empty data for save.")
		else:
			user_id = self.users.insert_one(data).inserted_id
			print(f"insert_user_in_db - {user_id}")
	
	def find_file_in_db(self, d_url):
		if d_url is None:
			raise Exception(f"empty f_name")
		else:
			finded_file = self.files.find_one({"downloaded_url":d_url})
			return finded_file

	def find_user_in_db(self, u_name):
		if u_name is None:
			raise Exception(f"empty u_name")
		else:
			finded_user = self.users.find_one({"user_name":u_name})
			return finded_user
	
	#think about delete_one or delete_many
	def delete_file_in_db(self, f_name):
		if f_name is None:
			raise Exception(f"empty f_name")
		result = self.files.delete_one({"file_name":f_name})
		if result["acknowledged"]:
			print(f"result delete_file_in_db - {result}")
		else:
			print(f"can't delete this obj")

	def delete_user_in_db(self, u_name):
		if u_name is None:
			raise Exception(f"empty f_name")
		result = self.files.delete_one({"user_name":u_name})
		if result["acknowledged"]:
			print(f"result delete_user_in_db - {result}")
		else:
			print(f"can't delete this obj")

	def update_file_in_db(self, f_name, data):
		if f_name is None:
			raise Exception(f"empty f_name")
		self.files.update_one({"file_name":f_name}, {"$set": data}, upsert=True)

	def update_user_in_db(self, u_name, data):
		if u_name is None:
			raise Exception(f"empty u_name")
		self.files.update_one({"user_name":u_name}, {"$set": data}, upsert=True)