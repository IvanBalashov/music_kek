import redis
import json

class StoreController(object):

	def __init__(self, my_host, my_port):
		pool = redis.ConnectionPool(host=my_host, port=my_port, db=0)
		self.red = redis.Redis(connection_pool=pool)

	def save_data_in_store(self, saved_name, data):
		"""save data in to redis"""
		try:
			print(f"data -  {data}")
			info = self.red.execute_command('JSON.SET', saved_name, '.', json.dumps(data))
			print(f"after execute - {info}")
		except Exception as e:
			print(f"exception in save_data_in_store - {e}")

	def get_full_obj_from_store(self, saved_name):
		"""find data in redis store and return him"""
		try:
			data = json.loads(self.red.execute_command('JSON.GET', saved_name))
			return data
		except Exception as e:
			print(f"exception in get_full_obj_from_store - {e}")
			return None

	def get_field_data_in_store(self, saved_name, field):
		"""find field in saved_name and return his value"""
		try:
			data = json.loads(self.red.execute_command('JSON.GET', saved_name, '.', field))
			return data
		except Exception as e:
			print(f"exception in get_full_obj_from_store - {e}")
			return None

	def delete_data_in_store(self, key):
		"""delete key:val obj from store"""
		try:
			count = self.red.execute_command('JSON.DEL', key)
			if count != 1:
				return None
			else:
				return count
		except Exception:
			return None
			