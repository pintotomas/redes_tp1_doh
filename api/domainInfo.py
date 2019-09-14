from itertools import cycle

class DomainInfo:

	def __init__(self, ip_array, custom):
		self.ip_list = cycle(ip_array)
		self.custom = custom

	def change_ips(self, ip_array, custom):
		self.ip_list = cycle(ip_array)
		self.custom = custom

	def get_ip(self):
		return next(self.ip_list)

	def is_custom(self):
		return self.custom