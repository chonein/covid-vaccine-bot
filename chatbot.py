import requests
import json
import re
import threading
import time

API_KEY = "tTwOPEfNOXmB"  # "tTwOPEfNOXmB"
PROJECT_TOKEN = "ts9X3T1m_aCb"  # thkOKcyhxCmm"
RUN_TOKEN = "toi8Txr1XDon"  # "tVjyRecA5yuZ"


class Data:
    def __init__(self, api_key, project_token):
        self.api_key = api_key
        self.project_token = project_token
        self.params = {
            "api_key": self.api_key
        }
        self.data = self.get_data()

    def get_data(self):
        response = requests.get(
            f'https://www.parsehub.com/api/v2/projects/{self.project_token}/last_ready_run/data', params=self.params)
        data = json.loads(response.text)
        return data

    
    # WORLD and USA
    def getStoreData(self, key):
        return self.data[key]

    # CALIFORNIA
    def getStoreCaliData(self, key):
        data = self.data['covid_urls']
        return data[0][key]
    
    # CITIES
    def getStoreCityData(self, city, key):
        data = self.data['covid_urls']
        for content in data:
            if content['name'].lower() == city.lower():
                return content[key]
    
    # Get Cities in a list
    def get_city_list(self):
        city_list = []
        data = self.data['covid_urls']
        for content in data[1:]:
            city_list.append(content['name'].lower())
        return city_list
    
    # def get_country_data(self, country):
    #     data = self.data["country"]

    #     for content in data:
    #         if content['name'].lower() == country.lower():
    #             return content
    #     return "0"

    # def get_list_of_countries(self):
    #     countries = []
    #     for country in self.data['country']:
    #         countries.append(country['name'].lower())
    #     return countries

    def update_data(self):
        response = requests.post(
            f'https://www.parsehub.com/api/v2/projects/{self.project_token}/run', params=self.params)

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

    thisData = Data(API_KEY, PROJECT_TOKEN)
    END_PHRASE = "stop"
    # country_list = data.get_list_of_countries()

    '''
    Guideline: 
    total_cases
    new_cases
    total_deaths
    new_deaths
    total_recovered
    active_cases
    '''
    TOTAL_PATTERNS = {
        # WORLD
        # Total Cases
        re.compile("[\w\s]+ total [\w\s]+ cases"): lambda: thisData.getStoreData('world_total_cases'),
        re.compile("[\w\s]+ total cases"): lambda: thisData.getStoreData('world_total_cases'),
        
        # New Cases
        re.compile("[\w\s]+ total new [\w\s]+ cases"): lambda: thisData.getStoreData('world_new_cases'),
        re.compile("[\w\s]+ total new cases"): lambda: thisData.getStoreData('world_new_cases'),
        
        # Total Deaths
        re.compile("[\w\s]+ total [\w\s]+ deaths"): lambda: thisData.getStoreData('world_total_deaths'),
        re.compile("[\w\s]+ total deaths"): lambda: thisData.getStoreData('world_total_deaths'),
        
        # New Deaths
        re.compile("[\w\s]+ total new [\w\s]+ deaths"): lambda: thisData.getStoreData('world_new_deaths'),
        re.compile("[\w\s]+ total new deaths"): lambda: thisData.getStoreData('world_new_deaths'),
        
        # Total Recovered
        re.compile("[\w\s]+ total [\w\s]+ recovered"): lambda: thisData.getStoreData('world_total_recovered'),
        re.compile("[\w\s]+ total recovered"): lambda: thisData.getStoreData('world_total_recovered'),

        # Active Cases
        re.compile("[\w\s]+ total active [\w\s]+ cases"): lambda: thisData.getStoreData('world_active_cases'),
        re.compile("[\w\s]+ total active cases"): lambda: thisData.getStoreData('world_active_cases'),      
    }

    USA_PATTERNS = {
        # US
        # Total Cases
        re.compile("[\w\s]+ us [\w\s]+ cases"): lambda: thisData.getStoreData('usa_total_cases'),
        re.compile("[\w\s]+ cases in [\w\s]+ us"): lambda: thisData.getStoreData('usa_total_cases'),
        re.compile("[\w\s]+ cases [\w\s]+ in [\w\s]+ us"): lambda: thisData.getStoreData('usa_total_cases'),
        re.compile("[\w\s]+ cases in us"): lambda: thisData.getStoreData('usa_total_cases'),
        
        # New Cases
        re.compile("[\w\s]+ us [\w\s]+ new cases"): lambda: thisData.getStoreData('usa_new_cases'),
        re.compile("[\w\s]+ new cases in [\w\s]+ us"): lambda: thisData.getStoreData('usa_new_cases'),
        re.compile("[\w\s]+ new cases [\w\s]+ in [\w\s]+ us"): lambda: thisData.getStoreData('usa_new_cases'),
        
        # Total Deaths
        re.compile("[\w\s]+ us [\w\s]+ deaths"): lambda: thisData.getStoreData('usa_total_deaths'),
        re.compile("[\w\s]+ deaths in [\w\s]+ us"): lambda: thisData.getStoreData('usa_total_deaths'),
        re.compile("[\w\s]+ deaths [\w\s]+ in [\w\s]+ us"): lambda: thisData.getStoreData('usa_total_deaths'),
        
        # New Deaths
        re.compile("[\w\s]+ us [\w\s]+ new deaths"): lambda: thisData.getStoreData('usa_new_deaths'),
        re.compile("[\w\s]+ new deaths in [\w\s]+ us"): lambda: thisData.getStoreData('usa_new_deaths'),
        re.compile("[\w\s]+ new deaths [\w\s]+ in [\w\s]+ us"): lambda: thisData.getStoreData('usa_new_deaths'),
        
        # Total Recovered
        re.compile("[\w\s]+ us [\w\s]+ recovered"): lambda: thisData.getStoreData('usa_total_recovered'),
        re.compile("[\w\s]+ recovered in [\w\s]+ us"): lambda: thisData.getStoreData('usa_total_recovered'),
        re.compile("[\w\s]+ recovered [\w\s]+ in [\w\s]+ us"): lambda: thisData.getStoreData('usa_total_recovered'),

        # Active Cases
        re.compile("[\w\s]+ us [\w\s]+ active cases"): lambda: thisData.getStoreData('usa_active_cases'),
        re.compile("[\w\s]+ active cases in [\w\s]+ us"): lambda: thisData.getStoreData('usa_active_cases'),
        re.compile("[\w\s]+ active cases [\w\s]+ in [\w\s]+ us"): lambda: thisData.getStoreData('usa_active_cases'),

        # Total Tests
        re.compile("[\w\s]+ us [\w\s]+ tests"): lambda: thisData.getStoreData('usa_total_tests'),
        re.compile("[\w\s]+ tests in [\w\s]+ us"): lambda: thisData.getStoreData('usa_total_tests'),
        re.compile("[\w\s]+ tests [\w\s]+ in [\w\s]+ us"): lambda: thisData.getStoreData('usa_total_tests'),
    }

    CALIFORNIA_PATTERNS = {
        # CALIFORNIA
        # Total Cases
        re.compile("[\w\s]+ cases in california"): lambda: thisData.getStoreCaliData('total_cases'),
        re.compile("[\w\s]+ cases in [\w\s]+ california"): lambda: thisData.getStoreCaliData('total_cases'),
        
        # New Cases
        re.compile("[\w\s]+ new [\w\s]+ cases in california"): lambda: thisData.getStoreCaliData('new_cases'),
        re.compile("[\w\s]+ new cases in [\w\s]+ california"): lambda: thisData.getStoreCaliData('new_cases'),
        
        # Total Deaths
        re.compile("[\w\s]+ [\w\s]+ deaths in california"): lambda: thisData.getStoreCaliData('total_deaths'),
        re.compile("[\w\s]+ deaths in [\w\s]+ california"): lambda: thisData.getStoreCaliData('total_deaths'),
        
        # New Deaths
        re.compile("[\w\s]+ new [\w\s]+ deaths in california"): lambda: thisData.getStoreCaliData('new_deaths'),
        re.compile("[\w\s]+ deaths in [\w\s]+ california"): lambda: thisData.getStoreCaliData('new_deaths'),
        
        # Total Recovered
        re.compile("[\w\s]+ recovered [\w\s]+ in california"): lambda: thisData.getStoreCaliData('total_recovered'),
        re.compile("[\w\s]+ recovered in [\w\s]+ california"): lambda: thisData.getStoreCaliData('total_recovered'),

        # Active Cases
        re.compile("[\w\s]+ active [\w\s]+ cases in california"): lambda: thisData.getStoreCaliData('active_cases'),
        re.compile("[\w\s]+ active cases in [\w\s]+ california"): lambda: thisData.getStoreCaliData('active_cases'),

        # Total Tests
        re.compile("[\w\s]+ tests [\w\s]+ in california"): lambda: thisData.getStoreCaliData('total_tests'),
        re.compile("[\w\s]+ tests in [\w\s]+ california"): lambda: thisData.getStoreCaliData('total_tests'),
    }

    CITY_PATTERNS = {
        # CITIES
        # Total Cases
        re.compile("[\w\s]+ cases [\w\s]+ in [\w\s]+"): lambda city: thisData.getStoreCityData(city, 'total_cases'),
        
        # New Cases
        re.compile("[\w\s]+ new [\w\s]+ cases [\w\s]+ in [\w\s]+"): lambda city: thisData.getStoreCityData(city, 'new_cases'),
        
        # Total Deaths
        re.compile("[\w\s]+ [\w\s]+ deaths [\w\s]+ in [\w\s]+"): lambda city: thisData.getStoreCityData(city, 'total_deaths'),
        
        # New Deaths
        re.compile("[\w\s]+ new [\w\s]+ deaths [\w\s]+ in [\w\s]+"): lambda city: thisData.getStoreCityData(city, 'new_deaths'),
        
        # Total Recovered
        re.compile("[\w\s]+ recovered [\w\s]+ in [\w\s]+"): lambda city: thisData.getStoreCityData(city, 'total_recovered'),

        # Active Cases
        re.compile("[\w\s]+ active [\w\s]+ cases [\w\s]+ in [\w\s]+"): lambda city: thisData.getStoreCityData(city, 'active_cases'),

        # Total Tests
        re.compile("[\w\s]+ tests [\w\s]+ in [\w\s]+"): lambda: thisData.getStoreCityData(city, 'total_tests'),
    }

    UPDATE_COMMAND = "update"

    print("Listening...")
    text = phrase
    print(text)
    result = "I'm sorry, I don't understand that phrase."

    # for pattern, func in COUNTRY_PATTERNS.items():
    #     if pattern.match(text):
    #         words = set(text.lower().split(" "))
    #         for country in country_list:
    #             if country in words:
    #                 result = func(country)
    #                 if country == "usa":
    #                     country = "the U.S."
    #                 return "There are %s cases in %s." % (result, country)

    city_list = thisData.get_city_list()
    print(city_list)
    
    for pattern, func in CITY_PATTERNS.items():
        if pattern.match(text):
            words = set(text.lower().split(" "))
        for city in city_list:
            if city in words:
                result = func(city)
                return "There are %s cases in %s." % (result, city)

    for pattern, func in CALIFORNIA_PATTERNS.items():
        if pattern.match(text):
            return func()
    
    for pattern, func in USA_PATTERNS.items():
        if pattern.match(text):
            print("match!")
            return func()

    for pattern, func in TOTAL_PATTERNS.items():
        if pattern.match(text):
            return func()
    
    if text == UPDATE_COMMAND:
        result = "Data is being updated. This may take a moment!"
        thisData.update_data()
    return result


if __name__ == "__main__":
    # phrase = "How many total cases are there"
    # phrase = "How many total cases are there in Canada"
    # phrase = "How many total cases are there in USA"
    # phrase = "How many total cases are there in Argentina"
    # phrase = "How many total deaths are there"
    # phrase = "How many cases in california"
    phrase = "how many cases in the us"
    ans = main(phrase)
    print(ans)
