import requests


class Lab():
	def __init__(self,ip=None,port=8080,illumina_endpoint="illumina/",csv_endpoint="csv/",
												upload_endpoint="upload/",run_endpoint="run/"):
		if ip:
			self._server 			= "http://%s:%s/"%(ip,port)
			self._illumina_endpoint = illumina_endpoint
			self._csv_endpoint 		= csv_endpoint
			self._upload_endpoint 	= upload_endpoint
			self._run_endpoint 		= run_endpoint

	def get_experiment(self):
		pass

	def get_illumina(self):
		return requests.get(server+_illumina_endpoint)

	def get_csv_list(self):
		return requests.get(server+_csv_endpoint)

	def get_status(self):
		pass

	def get_running(self):
		pass

	def get_hub_url(self):
		pass

	def update_illumina(self):
		pass

	def upload_csv(self):
		pass

	def run():
		pass
