import redis
import json

class StoreController(object):

	def __init__(self, my_host, my_port):
		#pool = redis.ConnectionPool(host=my_host, port=my_port, db=0)
		print(f"connect to redis")
		self.red = redis.Redis(host=my_host, port=my_port, db=0)
		try:
			info = self.red.execute_command('PING')
			if info:
				print(f"connected to redis server")
			else:
				print(f"can't connect to redis server")
		except Exception as e:
			print(f"error in connect - {e}")

	def save_data_in_store(self, saved_name, data) -> bool:
		"""save data in to redis"""
		if saved_name is None:
			return False
		try:
			info = self.red.execute_command('JSON.SET', saved_name, '.', json.dumps(data))
			if info.decode("utf-8") == "OK":
				return True
			else:
				return False
		except Exception as e:
			print(f"exception in save_data_in_store - {e}")

	def get_full_obj_from_store(self, saved_name) -> dict:
		"""find data in redis store and return him"""
		if saved_name is None:
			return None
		try:
			data = json.loads(self.red.execute_command('JSON.GET', saved_name))
			return data
		except Exception as e:
			print(f"exception in get_full_obj_from_store - {e}")
			return None

	def get_field_data_in_store(self, saved_name, field) -> dict:
		"""find field in saved_name and return his value"""
		try:
			data = json.loads(self.red.execute_command('JSON.GET', saved_name, '.', field))
			return data
		except Exception as e:
			print(f"exception in get_full_obj_from_store - {e}")
			return None

	def delete_data_in_store(self, key) -> None:
		"""delete key:val obj from store"""
		if key is None:
			return None
		try:
			count = self.red.execute_command('JSON.DEL', key)
			print(f"deleted obj count - {count}")
			if count != 1:
				return None
			else:
				return count
		except Exception as e:
			print(f"exception in delete_data_in_store - {e}")
			return None
