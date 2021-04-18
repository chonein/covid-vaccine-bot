import requests
import json
import re
import threading
import time
import string

API_KEY = "tTwOPEfNOXmB"
PROJECT_TOKEN = "ts9X3T1m_aCb"
RUN_TOKEN = "tgNTTV9TKzkz" # "toi8Txr1XDon"
startTime = time.time()
auto_update = False


class Data:
    def __init__(self, api_key, project_token):
        self.api_key = api_key
        self.project_token = project_token
        self.params = { "api_key": self.api_key }
        self.data = self.get_data()

    def get_data(self):
        response = requests.get(
            f'https://www.parsehub.com/api/v2/projects/{self.project_token}/last_ready_run/data', params=self.params)
        data = json.loads(response.text)
        return data
    
    # TIMESTAMP
    def getTimestamp(self):
        data = self.data['timestamp']
        return data

    # WORLD and USA
    def getStoreData(self, key):
        try:
            return self.data[key], key
        except KeyError:
            return 0, 0
        except:
            return None, None

    # CALIFORNIA
    def getStoreCaliData(self, key):
        data = self.data['covid_urls']
        try:
            return data[0][key], key
        except KeyError:
            return 0, 0
        except:
            return None, None
    
    # CITIES
    def getStoreCityData(self, find_city, key):
        
        data = self.data['covid_urls']
        try:
            for content in data:
                for city in content['cities']:
                    if city['name'].lower() == find_city.lower():
                        return city[key], key, city['name']
        except KeyError:
            return 0, 0, 0
        except:
            return None, None, None
    
    # Get Cities in a list
    def get_city_list(self):
        city_list = []
        data = self.data['covid_urls']
        for content in data:
            for city in content['cities']:
                city_list.append(city['name'].lower())
        return city_list

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
                    print("Data updated!")
                    break
                time.sleep(5)

        t = threading.Thread(target=poll)
        t.start()


def transcribe_response(pattern_items, text, city_list):
    for pattern, func in pattern_items:
        if pattern.match(text):
            words = text.lower()
            result, request, city_name = None, None, None
            try:
                result, request = func()
                # if request == 'total_cases':
                if (result != 0 and request != 0) and (request.find('world') == -1 or request.find('usa') == -1):
                    city_name = 'California'
            
            except ValueError:
                result = func()
            except TypeError:
                for city in city_list:
                    if city in words:
                        result, request, city_name = func(city)
            if result == None and (request == None or city_name == None): # case when nothing reads
                return "An internal error occurred."
            if result == 0 and request == 0: # case if no data found
                return False
            if request == None: # case when asking for the last update time
                return result
            location, id_type = parse_name(request)
            if location == None:
                location, id_type = city_name, ''
            if request == (id_type + 'total_cases'):
                return "There have been a total of %s cases in %s." % (result, location)
            elif request == (id_type + 'new_cases'):
                return "There have been a total of %s new cases in %s today." % (result, location)
            elif request == (id_type + 'total_deaths'):
                return "There have been a total of %s deaths in %s." % (result, location)
            elif request == (id_type + 'new_deaths'):
                return "There have been a total of %s new deaths in %s today." % (result, location)
            elif request == (id_type + 'total_recovered'):
                return "There have been a total of %s people recovered in %s." % (result, location)
            elif request == (id_type + 'active_cases'):
                return "There are a total of %s active cases in %s." % (result, location)
            elif request == (id_type + 'total_tests'):
                return "There are have been a total of %s tests given in %s." % (result, location)

def parse_name(request):
    location = request
    if request.find('_') != -1:
        location = request[:request.find('_')]
    if location == 'usa':
        return 'United States', 'usa_'
    elif location == 'world':
        return 'the world', 'world_'
    return None, None

def main(question: str):
    """ takes in question from user, then trasnslates an answer """
    print("Started Program")

    thisData = Data(API_KEY, PROJECT_TOKEN)

    TIMESTAMP_PATTERNS = {
        # TIMESTAMP
        re.compile("[\w\s]+ last [\w\s]+ updated"): lambda: thisData.getTimestamp(),
        re.compile("[\w\s]+ last updated"): lambda: thisData.getTimestamp(),
        re.compile("[\w\s]+ update [\w\s]+ "): lambda: thisData.getTimestamp(),
    }

    TOTAL_PATTERNS = {
        # WORLD
        # New Cases
        re.compile("[\w\s]+ total new [\w\s]+ cases"): lambda: thisData.getStoreData('world_new_cases'),
        re.compile("[\w\s]+ total new cases"): lambda: thisData.getStoreData('world_new_cases'),
        re.compile("[\w\s]+ new [\w\s]+ cases [\w\s]+ world"): lambda: thisData.getStoreData('world_new_cases'),
        re.compile("[\w\s]+ new [\w\s]+ world cases"): lambda: thisData.getStoreData('world_new_cases'),

        # New Deaths
        re.compile("[\w\s]+ total new [\w\s]+ deaths"): lambda: thisData.getStoreData('world_new_deaths'),
        re.compile("[\w\s]+ total new deaths"): lambda: thisData.getStoreData('world_new_deaths'),

        # Total Recovered
        re.compile("[\w\s]+ total [\w\s]+ recovered"): lambda: thisData.getStoreData('world_total_recovered'),
        re.compile("[\w\s]+ total recovered"): lambda: thisData.getStoreData('world_total_recovered'),

        # Active Cases
        re.compile("[\w\s]+ total active [\w\s]+ cases"): lambda: thisData.getStoreData('world_active_cases'),
        re.compile("[\w\s]+ total active cases"): lambda: thisData.getStoreData('world_active_cases'),

        # Total Tests
        re.compile("[\w\s]+ total [\w\s]+ tests"): lambda: thisData.getStoreData('world_total_tests'),
        re.compile("[\w\s]+ total tests in [\w\s]"): lambda: thisData.getStoreData('world_total_tests'),
        re.compile("[\w\s]+ total tests [\w\s]+ in [\w\s]"): lambda: thisData.getStoreData('world_total_tests'),

        # Total Cases
        re.compile("[\w\s]+ total [\w\s]+ cases"): lambda: thisData.getStoreData('world_total_cases'),
        re.compile("[\w\s]+ total cases"): lambda: thisData.getStoreData('world_total_cases'),

        # Total Deaths
        re.compile("[\w\s]+ total [\w\s]+ deaths"): lambda: thisData.getStoreData('world_total_deaths'),
        re.compile("[\w\s]+ total deaths"): lambda: thisData.getStoreData('world_total_deaths'),

    }

    USA_PATTERNS = {
        # US
        # New Cases
        re.compile("[\w\s]+ us [\w\s]+ new cases"): lambda: thisData.getStoreData('usa_new_cases'),
        re.compile("[\w\s]+ new cases in [\w\s]+ us"): lambda: thisData.getStoreData('usa_new_cases'),
        re.compile("[\w\s]+ new cases [\w\s]+ in [\w\s]+ us"): lambda: thisData.getStoreData('usa_new_cases'),

        # Total Recovered
        re.compile("[\w\s]+ us [\w\s]+ recovered"): lambda: thisData.getStoreData('usa_total_recovered'),
        re.compile("[\w\s]+ recovered in [\w\s]+ us"): lambda: thisData.getStoreData('usa_total_recovered'),
        re.compile("[\w\s]+ recovered [\w\s]+ in [\w\s]+ us"): lambda: thisData.getStoreData('usa_total_recovered'),
        re.compile("[\w\s]+ recovered in us"): lambda: thisData.getStoreData('usa_total_recovered'),
        re.compile("[\w\s]+ recovered [\w\s]+ in us"): lambda: thisData.getStoreData('usa_total_recovered'),

        # Total Cases
        re.compile("[\w\s]+ us [\w\s]+ cases"): lambda: thisData.getStoreData('usa_total_cases'),
        re.compile("[\w\s]+ cases in [\w\s]+ us"): lambda: thisData.getStoreData('usa_total_cases'),
        re.compile("[\w\s]+ cases [\w\s]+ in [\w\s]+ us"): lambda: thisData.getStoreData('usa_total_cases'),
        re.compile("[\w\s]+ cases in us"): lambda: thisData.getStoreData('usa_total_cases'),

        # Total Deaths
        re.compile("[\w\s]+ us [\w\s]+ deaths"): lambda: thisData.getStoreData('usa_total_deaths'),
        re.compile("[\w\s]+ deaths in [\w\s]+ us"): lambda: thisData.getStoreData('usa_total_deaths'),
        re.compile("[\w\s]+ deaths [\w\s]+ in [\w\s]+ us"): lambda: thisData.getStoreData('usa_total_deaths'),
        
        # New Deaths
        re.compile("[\w\s]+ us [\w\s]+ new deaths"): lambda: thisData.getStoreData('usa_new_deaths'),
        re.compile("[\w\s]+ new deaths in [\w\s]+ us"): lambda: thisData.getStoreData('usa_new_deaths'),
        re.compile("[\w\s]+ new deaths [\w\s]+ in [\w\s]+ us"): lambda: thisData.getStoreData('usa_new_deaths'),

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
        # New Cases
        re.compile("[\w\s]+ new [\w\s]+ cases in california"): lambda: thisData.getStoreCaliData('new_cases'),
        re.compile("[\w\s]+ new cases in [\w\s]+ california"): lambda: thisData.getStoreCaliData('new_cases'),
        re.compile("[\w\s]+ new cases in california"): lambda: thisData.getStoreCaliData('new_cases'),
        
        # Active Cases
        re.compile("[\w\s]+ active [\w\s]+ cases in california"): lambda: thisData.getStoreCaliData('active_cases'),
        re.compile("[\w\s]+ active cases in [\w\s]+ california"): lambda: thisData.getStoreCaliData('active_cases'),
        re.compile("[\w\s]+ active [\w\s]+ in california"): lambda: thisData.getStoreCaliData('active_cases'),

        # Total Recovered
        re.compile("[\w\s]+ recovered [\w\s]+ in california"): lambda: thisData.getStoreCaliData('total_recovered'),
        re.compile("[\w\s]+ recovered in [\w\s]+ california"): lambda: thisData.getStoreCaliData('total_recovered'),
        re.compile("[\w\s]+ recovered in california"): lambda: thisData.getStoreData('usa_total_recovered'),
        re.compile("[\w\s]+ recovered [\w\s] + in california"): lambda: thisData.getStoreData('usa_total_recovered'),

        # New Deaths
        re.compile("[\w\s]+ new [\w\s]+ deaths in california"): lambda: thisData.getStoreCaliData('new_deaths'),
        re.compile("[\w\s]+ new deaths in california"): lambda: thisData.getStoreCaliData('new_deaths'),
        re.compile("[\w\s]+ deaths in [\w\s]+ california"): lambda: thisData.getStoreCaliData('new_deaths'),

        # Total Cases
        re.compile("[\w\s]+ cases in california"): lambda: thisData.getStoreCaliData('total_cases'),
        re.compile("[\w\s]+ cases in [\w\s]+ california"): lambda: thisData.getStoreCaliData('total_cases'),

        # Total Deaths
        re.compile("[\w\s]+ [\w\s]+ deaths in california"): lambda: thisData.getStoreCaliData('total_deaths'),
        re.compile("[\w\s]+ deaths in [\w\s]+ california"): lambda: thisData.getStoreCaliData('total_deaths'),

        # Total Tests
        re.compile("[\w\s]+ tests [\w\s]+ in california"): lambda: thisData.getStoreCaliData('total_tests'),
        re.compile("[\w\s]+ tests in [\w\s]+ california"): lambda: thisData.getStoreCaliData('total_tests'),
    }

    CITY_PATTERNS = {
        # CITIES
        
        # Total Recovered
        re.compile("[\w\s]+ recovered [\w\s]+ in [\w\s]+"): lambda city: thisData.getStoreCityData(city, 'total_recovered'),
        
        # Total Tests
        re.compile("[\w\s]+ tests [\w\s]+ in [\w\s]+"): lambda city: thisData.getStoreCityData(city, 'total_tests'),
        
        # Active Cases
        re.compile("[\w\s]+ active [\w\s]+ cases [\w\s]+ in [\w\s]+"): lambda city: thisData.getStoreCityData(city, 'active_cases'),

                
        # New Deaths
        re.compile("[\w\s]+ new [\w\s]+ deaths [\w\s]+ in [\w\s]+"): lambda city: thisData.getStoreCityData(city, 'new_deaths'),
        
        # New Cases
        re.compile("[\w\s]+ new [\w\s]+ cases [\w\s]+ in [\w\s]+"): lambda city: thisData.getStoreCityData(city, 'new_cases'),

        # Total Cases
        re.compile("[\w\s]+ cases [\w\s]+ in [\w\s]+"): lambda city: thisData.getStoreCityData(city, 'total_cases'),
        re.compile("[\w\s]+ cases in [\w\s]+"): lambda city: thisData.getStoreCityData(city, 'total_cases'),
        
        # Total Deaths
        re.compile("[\w\s]+ [\w\s]+ deaths [\w\s]+ in [\w\s]+"): lambda city: thisData.getStoreCityData(city, 'total_deaths'),
    }

    UPDATE_COMMAND = "update"
    for punc in string.punctuation:
        question = question.replace(punc, '')

    text = question
    result = "I'm sorry, I don't understand that phrase."

    city_list = thisData.get_city_list()
    pattern_list = [TIMESTAMP_PATTERNS, TOTAL_PATTERNS, USA_PATTERNS, CALIFORNIA_PATTERNS, CITY_PATTERNS]
    for pattern in pattern_list:
        response = transcribe_response(pattern.items(), text, city_list)
        if response == False:
            for pattern, func in TIMESTAMP_PATTERNS.items():
                text = "when was it last updated"
                pattern.match(text)
                result = func()
                return "No data found for this request. %s" % (result)
        if response != None:
            return response
             
    if auto_update and time.time() - startTime <= 3600:
        result = "Data is being updated. This may take a moment!"
        startTime = time.time()
        thisData.update_data()
    return result


if __name__ == "__main__":
    phrase = "How many total new cases are there"
    # phrase = "How many total cases are there in Canada"
    # phrase = "How many total cases are there in USA"
    # phrase = "How many total cases are there in Argentina"
    # phrase = "How many total deaths are there"
    # phrase = "How many cases in california"
    # phrase = "how many cases in napa"
    phrase = "How many total ca,ses i*n u-s?"
    phrase = "How many cases in napa"
    phrase = "How many total new cases in the world"
    # phrase = "When was it last updated"
    # phrase = "How many new cases in california"
    phrase = "How many recovered cases in us"
    ans = main(phrase)
    print(ans)
