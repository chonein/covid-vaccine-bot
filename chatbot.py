import requests
import json
import re
import threading
import time

API_KEY = "tTwOPEfNOXmB"
PROJECT_TOKEN = "thkOKcyhxCmm"
RUN_TOKEN = "tVjyRecA5yuZ"


class Data:
	def __init__(self, api_key, project_token):
		self.api_key = api_key
		self.project_token = project_token
		self.params = {
			"api_key": self.api_key
		}
		self.data = self.get_data()

	def get_data(self):
		response = requests.get(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/last_ready_run/data', params=self.params)
		data = json.loads(response.text)
		return data

	def get_total_cases(self):
		data = self.data['total']
		for content in data:
			if content['name'] == "Coronavirus Cases:":
				return content['value']

	def get_total_deaths(self):
		data = self.data['total']
		for content in data:
			if content['name'] == "Deaths:":
				return content['value']
		return "0"


	def get_country_data(self, country):
		data = self.data["country"]

		for content in data:
			if content['name'].lower() == country.lower():
				return content
		return "0"

	def get_list_of_countries(self):
		countries = []
		for country in self.data['country']:
			countries.append(country['name'].lower())
		return countries
	
	def get_active_cases(self):
    	pass

	def update_data(self):
		response = requests.post(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/run', params=self.params)

		def poll():
			time.sleep(0.1)
			old_data = self.data
			while True:
				new_data = self.get_data()
				if new_data != old_data:
					self.data = new_data
					print("Data updated")
					break
				time.sleep(5)


		t = threading.Thread(target=poll)
		t.start()
    	
def main(question: str):
	""" takes in question from user, then trasnslates an answer """
	print("Started Program")
	
	data = Data(API_KEY, PROJECT_TOKEN)
	END_PHRASE = "stop"
	country_list = data.get_list_of_countries()

	TOTAL_PATTERNS = {
					# Total Cases
					re.compile("[\w\s]+ total [\w\s]+ cases"):data.get_total_cases,
					re.compile("[\w\s]+ total cases"): data.get_total_cases,
					# Total Deaths
                    re.compile("[\w\s]+ total [\w\s]+ deaths"): data.get_total_deaths,
                    re.compile("[\w\s]+ total deaths"): data.get_total_deaths
					}

	COUNTRY_PATTERNS = {
					re.compile("[\w\s]+ cases [\w\s]+"): lambda country: data.get_country_data(country)['cases'],
                    re.compile("[\w\s]+ deaths [\w\s]+"): lambda country: data.get_country_data(country)['total_deaths'],
					}

	UPDATE_COMMAND = "update"

	print("Listening...")
	text = phrase
	print(text)
	result = "I'm sorry, I don't understand that phrase."

	for pattern, func in COUNTRY_PATTERNS.items():
		if pattern.match(text):
			words = set(text.lower().split(" "))
			for country in country_list:
				if country in words:
					result = func(country)
					if country == "usa":
						country = "the U.S."
					return "There are %s cases in %s." % (result, country)

	for pattern, func in TOTAL_PATTERNS.items():
		if pattern.match(text):
			return func()

	if text == UPDATE_COMMAND:
		result = "Data is being updated. This may take a moment!"
		data.update_data()
	return result
		
if __name__ == "__main__":
	phrase = "How many total cases are there"
	phrase = "How many total cases are there in Canada"
	phrase = "How many total cases are there in USA"
	phrase = "How many total cases are there in Argentina"
	ans = main(phrase)
	print(ans)
