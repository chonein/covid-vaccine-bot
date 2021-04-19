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
    
    # GET HELP
    def getHelp(self):
        help_txt = "Some questions you can ask me are:\n" +\
                    "How many total cases are there?\n" +\
                    "How many new cases are there?\n" +\
                    "Give me the deaths in the US.\n" +\
                    "How many new deaths have there been in the US\n?" +\
                    "How many people have recovered from COVID in California?\n" +\
                    "Give me the number of active cases in San Luis Obispo.\n" +\
                    "How many tests have been given in Santa Clara?\n"
        return help_txt
        
        
    
    # TIMESTAMP
    def getTimestamp(self):
        print('here12')
        data = self.data['timestamp']
        return data

    # WORLD and USA
    def getStoreData(self, key):
        try:
            print('here11')
            return self.data[key], key
        except KeyError:
            return 0, 0
        except:
            return None, None

    # CALIFORNIA
    def getStoreCaliData(self, key):
        data = self.data['covid_urls']
        try:
            print('here10')
            return data[0][key], key
        except KeyError:
            return 0, 0
        except:
            return None, None
    
    # CITIES
    def getStoreCityData(self, find_city, key):
        
        data = self.data['covid_urls']
        try:
            print('here13')
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
            result, request, city_name = None, None, None
            try:
                result, request = func()

                # if request == 'total_cases':
                if (result != 0 and request != 0) and (request.find('world') == -1 or request.find('usa') == -1):
                    city_name = 'California'
            
            except ValueError:
                print('here2')
                result = func()
            except TypeError:
                print('here1')
                for city in city_list:
                    if city in text:
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


def add_chr_to_text(text: str):
    new_text = 'a '
    char = 'a'
    
    us_list = ['u.s', 'usa', 'u.s.a', 'u.s.', 'u.s.a.', 'united states']
    for us in us_list:
        text = text.replace(us, 'us')
    
    split = text.split()
    world = False
    key_list = ['world', 'global', 'globally', 'worldwide', 'international', 'internatonally']
    if split[-1] == 'there' and split[-2] == 'are':
        world = True

    for word in split:
        if word in key_list:
            world = True
        word += ' a '
        new_text += word
    return (new_text, world)



def main(question: str):
    """ takes in question from user, then trasnslates an answer """
    print("Started Program")

    thisData = Data(API_KEY, PROJECT_TOKEN)

    ASK_PATTERNS = {
        # ASK FOR HELP
        re.compile("[\w\s]+ help [\w\s]+ "): lambda: thisData.getHelp(),
        re.compile("[\w\s]+ help"): lambda: thisData.getHelp(),
        re.compile("help [\w\s]+"): lambda: thisData.getHelp(),
    }

    TIMESTAMP_PATTERNS = {
        # TIMESTAMP
        re.compile("[\w\s]+ updated [\w\s]+"): lambda: thisData.getTimestamp(),
        re.compile("[\w\s]+ update [\w\s]+ "): lambda: thisData.getTimestamp(),
    }

    TOTAL_PATTERNS = {
        # WORLD
        # Total Recovered
        re.compile("[\w\s]+ recovered [\w\s]+"): lambda: thisData.getStoreData('world_total_recovered'),

        # Active Cases
        re.compile("[\w\s]+ active [\w\s]+"): lambda: thisData.getStoreData('world_active_cases'),

        # Total Tests
        re.compile("[\w\s]+ tests [\w\s]+"): lambda: thisData.getStoreData('world_total_tests'),

        # New Cases
        re.compile("[\w\s]+ new [\w\s]+ cases [\w\s]+"): lambda: thisData.getStoreData('world_new_cases'),

        # New Deaths
        re.compile("[\w\s]+ new [\w\s]+ deaths [\w\s]+"): lambda: thisData.getStoreData('world_new_deaths'),

        # Total Cases
        re.compile("[\w\s]+ cases [\w\s]+"): lambda: thisData.getStoreData('world_total_cases'),

        # Total Deaths
        re.compile("[\w\s]+ deaths [\w\s]+"): lambda: thisData.getStoreData('world_total_deaths'),
    }

    USA_PATTERNS = {
        # US
         # Total Recovered
        re.compile("[\w\s]+ us [\w\s]+ recovered [\w\s]+"): lambda: thisData.getStoreData('usa_total_recovered'),
        re.compile("[\w\s]+ recovered [\w\s]+ us [\w\s]+"): lambda: thisData.getStoreData('usa_total_recovered'),
       
        # Active Cases
        re.compile("[\w\s]+ us [\w\s]+ active [\w\s]+ cases [\w\s]+"): lambda: thisData.getStoreData('usa_active_cases'),
        re.compile("[\w\s]+ active [\w\s]+ cases [\w\s]+ us [\w\s]+"): lambda: thisData.getStoreData('usa_active_cases'),
        re.compile("[\w\s]+ cases [\w\s]+ active [\w\s]+ us [\w\s]+"): lambda: thisData.getStoreData('usa_active_cases'),
        
         # Total Tests
        re.compile("[\w\s]+ us [\w\s]+ tests [\w\s]+"): lambda: thisData.getStoreData('usa_total_tests'),
        re.compile("[\w\s]+ tests [\w\s]+ us [\w\s]+"): lambda: thisData.getStoreData('usa_total_tests'),

        # New Cases
        re.compile("[\w\s]+ us [\w\s]+ new [\w\s]+ cases [\w\s]+"): lambda: thisData.getStoreData('usa_new_cases'),
        re.compile("[\w\s]+ new [\w\s]+ cases [\w\s]+ us [\w\s]+"): lambda: thisData.getStoreData('usa_new_cases'),

        # New Deaths
        re.compile("[\w\s]+ us [\w\s]+ new [\w\s]+ deaths [\w\s]+"): lambda: thisData.getStoreData('usa_new_deaths'),
        re.compile("[\w\s]+ new [\w\s]+ deaths [\w\s]+ us [\w\s]+"): lambda: thisData.getStoreData('usa_new_deaths'),
        re.compile("[\w\s]+ deaths [\w\s]+ new [\w\s]+ us [\w\s]+"): lambda: thisData.getStoreData('usa_new_deaths'),

        # Total Cases
        re.compile("[\w\s]+ us [\w\s]+ cases [\w\s]+"): lambda: thisData.getStoreData('usa_total_cases'),
        re.compile("[\w\s]+ cases [\w\s]+ us [\w\s]+"): lambda: thisData.getStoreData('usa_total_cases'),

        # Total Deaths
        re.compile("[\w\s]+ us [\w\s]+ deaths [\w\s]+"): lambda: thisData.getStoreData('usa_total_deaths'),
        re.compile("[\w\s]+ deaths [\w\s]+ us [\w\s]+"): lambda: thisData.getStoreData('usa_total_deaths'),
    }

    CALIFORNIA_PATTERNS = {
        # CALIFORNIA
        # Total Recovered
        re.compile("[\w\s]+ california [\w\s]+ recovered [\w\s]+"): lambda: thisData.getStoreData('usa_total_recovered'),
        re.compile("[\w\s]+ recovered [\w\s]+ california [\w\s]+"): lambda: thisData.getStoreCaliData('total_recovered'),

        # Active Cases
        re.compile("[\w\s]+ california [\w\s]+ active [\w\s]+"): lambda: thisData.getStoreCaliData('active_cases'),
        re.compile("[\w\s]+ active [\w\s]+ california [\w\s]+"): lambda: thisData.getStoreCaliData('active_cases'),

        # Total Tests
        re.compile("[\w\s]+ tests [\w\s]+ california [\w\s]+"): lambda: thisData.getStoreCaliData('total_tests'),
        re.compile("[\w\s]+ california [\w\s]+ tests[\w\s]+"): lambda: thisData.getStoreCaliData('total_tests'),

        # New Cases
        re.compile("[\w\s]+ california [\w\s]+ new [\w\s]+ cases [\w\s]+"): lambda: thisData.getStoreCaliData('new_cases'),
        re.compile("[\w\s]+ new [\w\s]+ cases [\w\s]+ california [\w\s]+"): lambda: thisData.getStoreCaliData('new_cases'),
        re.compile("[\w\s]+ cases [\w\s]+ new [\w\s]+ california [\w\s]+"): lambda: thisData.getStoreCaliData('new_cases'),
        
        # New Deaths
        re.compile("[\w\s]+ california [\w\s]+ new [\w\s]+ deaths [\w\s]+"): lambda: thisData.getStoreCaliData('new_deaths'),
        re.compile("[\w\s]+ new [\w\s]+ deaths [\w\s]+ california [\w\s]+"): lambda: thisData.getStoreCaliData('new_deaths'),
        re.compile("[\w\s]+ deaths [\w\s]+ new [\w\s]+ california [\w\s]+"): lambda: thisData.getStoreCaliData('new_deaths'),

        # Total Cases
        re.compile("[\w\s]+ cases [\w\s]+ california [\w\s]+"): lambda: thisData.getStoreCaliData('total_cases'),
        re.compile("[\w\s]+ california [\w\s]+ cases [\w\s]+"): lambda: thisData.getStoreCaliData('total_cases'),

        # Total Deaths
        re.compile("[\w\s]+ california [\w\s]+ deaths [\w\s]+"): lambda: thisData.getStoreCaliData('total_deaths'),
        re.compile("[\w\s]+ deaths [\w\s]+ california [\w\s]+"): lambda: thisData.getStoreCaliData('total_deaths'),
    }

    CITY_PATTERNS = {
        # CITIES
        # Total Recovered
        re.compile("[\w\s]+ recovered [\w\s]+"): lambda city: thisData.getStoreCityData(city, 'total_recovered'),
        
        # Active Cases
        re.compile("[\w\s]+ active [\w\s]+ cases [\w\s]+"): lambda city: thisData.getStoreCityData(city, 'active_cases'),
        re.compile("[\w\s]+ cases [\w\s]+ active [\w\s]+"): lambda city: thisData.getStoreCityData(city, 'active_cases'),
        
        # Total Tests
        re.compile("[\w\s]+ tests [\w\s]+"): lambda city: thisData.getStoreCityData(city, 'total_tests'),
        
        # New Cases
        re.compile("[\w\s]+ new [\w\s]+ cases [\w\s]+"): lambda city: thisData.getStoreCityData(city, 'new_cases'),
        re.compile("[\w\s]+ cases [\w\s]+ new [\w\s]+"): lambda city: thisData.getStoreCityData(city, 'new_cases'),

        # New Deaths
        re.compile("[\w\s]+ new [\w\s]+ deaths [\w\s]+"): lambda city: thisData.getStoreCityData(city, 'new_deaths'),
        re.compile("[\w\s]+ deaths [\w\s]+ new [\w\s]+"): lambda city: thisData.getStoreCityData(city, 'new_deaths'),
        
        # Total Cases
        re.compile("[\w\s]+ cases [\w\s]+"): lambda city: thisData.getStoreCityData(city, 'total_cases'),
        
        # Total Deaths
        re.compile("[\w\s]+ deaths [\w\s]+"): lambda city: thisData.getStoreCityData(city, 'total_deaths'),
    }

    UPDATE_COMMAND = "update"
    for punc in string.punctuation:
        question = question.replace(punc, '')

    text = question.lower()
    key = False
    text, key = add_chr_to_text(text)
    result = "I'm sorry, I don't understand that phrase."

    city_list = thisData.get_city_list()
    pattern_list = [ASK_PATTERNS, TIMESTAMP_PATTERNS, USA_PATTERNS, CALIFORNIA_PATTERNS, CITY_PATTERNS, TOTAL_PATTERNS]
    
    if key == True: # check if 'world' is in the word
        print('key is True')
        response = transcribe_response(TOTAL_PATTERNS.items(), text, city_list)
        if response == False:
            for pattern, func in TIMESTAMP_PATTERNS.items():
                text = "when was it last updated"
                pattern.match(text)
                result = func()
                return "No data found for this request. %s" % (result)
        elif response != None:
            return response
    
    else:
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
    # phrase = "How many cases are there"
    # phrase = "how many cases in napa"
    # phrase = "How many total ca,ses i*n u-s?"
    # phrase = "how many active cases are there"
    phrase = "how many new cases are in the us"
    # phrase = "how many  cases global"
    # phrase = "When was it last updated"
    # phrase = "How many new cases in california"
    # phrase = "can you help me"
    ans = main(phrase)
    print(ans)
