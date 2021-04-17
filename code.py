import time
import requests
import json
import signal
from math import radians, sin, cos, sqrt, atan2
import smtplib
import forms
import email_read
from typing import Any, Optional, Tuple

SENDER_EMAIL_ID = ''  # don't change
SENDER_EMAIL_ID_PASSWORD = ''  # don't change
REFRESH_PERIOD = 120  # Time period(in seconds) between program refreshes
TIME_BTWN_BACKUPS = 60*10
START_IDX_FNAME = 'start_idx.txt'
CHECKED_EMAILS_FNAME = 'num_checked_emails.txt'
ZIP_MAP_DICT: dict = dict()


def get_json_dict(url: str) -> dict:
    """ Function converts json file from the
    given url to a dictionary.
    """
    r = requests.get(url)
    jtext = r.text
    ca_d = json.loads(jtext)
    return ca_d


def write_to_json(url: str, jtext: str) -> None:
    """ Function is for debugging.
    Takes the input str from vaccine spotter website.
    """
    f_name = url[url.find('.json')-2:]
    with open(f_name, 'w') as out:
        out.write(jtext)


def earth_distance(lat1: float, lon1: float, lat2: float, lon2: float)\
        -> float:
    """ Calculate distance between to earth coordinates.
    Result is in miles.
    """
    # R = 6373.0  # earth radius in km
    R = 3963.0  # earth radius in miles
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance


def create_zip_dict() -> dict:
    """ Function creates a dictionary.
    the keys are the US zip codes.
    The data is the earth coordinates of that key.
    """
    with open('zip_coordinates.json', 'r') as zip_map:
        return json.loads(zip_map.read())


def active_providers(provider_info_list: list) -> set:
    """ Function uses the metadata to create a set of the active
    providers.
    """
    active_set = set()
    for provider in provider_info_list:
        if provider['status'] == 'active':
            active_set.add(provider['key'].lower())
    return active_set


def create_in_range_lst(source_features: list, zip_map_dict: dict,
                        user_zip_code: str, radius: int, active_set: set,
                        second_dose: bool) -> list:
    """ Create a list of the vaccination spots in range of user. """
    in_range_locs = []
    user_coords = zip_map_dict[user_zip_code]
    for loc in source_features:
        if loc['properties']['appointments_available'] and\
           loc['properties']['provider_brand'].lower() in active_set and\
           (loc['properties']['appointments_available_all_doses'] is True or
            loc['properties']['appointments_available_2nd_dose_only'] is
                second_dose):
            # format [latitude, longitude]
            loc_coord = loc['geometry']['coordinates'][::-1]
            if loc_coord != [None, None]:
                if earth_distance(loc_coord[0], loc_coord[1],
                                  user_coords[0], user_coords[1]) <= radius:
                    in_range_locs.append(loc)
    return in_range_locs


def create_message_list(in_range_list: list, user_zip_code: str,
                        zip_map_dict: dict) -> list:
    """ uses badly formatted in_range_list and converts it into
    a clean list of strings ready to be sent by email.
    """
    message_list = []
    user_coords = zip_map_dict[user_zip_code]
    for location in in_range_list:
        store_name = location['properties']['provider_brand_name']
        address = f"{location['properties']['address']}, " +\
                  f"{location['properties']['city']}, " +\
                  f"{location['properties']['state']}, " +\
                  f"{location['properties']['postal_code']}"
        loc_coord = location['geometry']['coordinates'][::-1]
        radius = str(earth_distance(loc_coord[0], loc_coord[1],
                                    user_coords[0], user_coords[1]))
        radius = radius[:radius.find('.')+2]
        url = location['properties']['url']
        message = f'{store_name}\n{address}\n' +\
                  f'Distance to store: {radius} miles\n{url}\n' +\
                  'Reply stop to stop these notifications.'
        message_list.append(message)
    return message_list


def get_data(radius: int, user_zip_code: str, state_dict: dict) -> list:
    """ Function calls the functions above to create a list of
    valid vaccination locations.
    """
    # zip_map_dict = create_zip_dict()
    active_set = active_providers(state_dict['metadata']['provider_brands'])
    in_range_lst = create_in_range_lst(state_dict['features'], ZIP_MAP_DICT,
                                       user_zip_code, radius,
                                       active_set, False)
    return create_message_list(in_range_lst, user_zip_code, ZIP_MAP_DICT)


def send_sms(phone_number: str, subject: str, body: str, carrier: str,
             carrier_emails: dict) -> None:
    """ Sends message through mms """
    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)
    receiver_email_id = f'{phone_number}@{carrier_emails[carrier]}'
    # start TLS for security
    s.starttls()
    # Authentication
    s.login(SENDER_EMAIL_ID, SENDER_EMAIL_ID_PASSWORD)

    message = ("From: %s\r\n" % SENDER_EMAIL_ID
               + "To: %s\r\n" % receiver_email_id
               + "Subject: %s\r\n" % subject
               + "\r\n"
               + body)

    # sending the mail
    s.sendmail(SENDER_EMAIL_ID, [receiver_email_id], message)
    # terminating the session
    s.quit()


def send_email(receiver_email_id: str, subject: str, body: str) -> None:
    """ Sends email """
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(str(SENDER_EMAIL_ID), str(SENDER_EMAIL_ID_PASSWORD))
    message = ("From: %s\r\n" % SENDER_EMAIL_ID
               + "To: %s\r\n" % receiver_email_id
               + "Subject: %s\r\n" % subject
               + "\r\n"
               + body)
    # sending the mail
    s.sendmail(SENDER_EMAIL_ID, [receiver_email_id], message)
    # terminating the session
    s.quit()


def add_phone_user(users_dict: dict, phone_number: str, radius: int,
                   user_zip_code: str, state: str, carrier: str) -> None:
    """ Adds user to users_dict where phone_number is the index. """
    if user_zip_code in ZIP_MAP_DICT:
        users_dict[phone_number] = {'radius': radius,
                                    'user_zip_code': user_zip_code,
                                    'state': state,
                                    'carrier': carrier,
                                    'usr_prevs_mes': [],
                                    'mes_limit': 150}


def add_email_user(users_dict: dict, receiver_email_id: str, radius: int,
                   user_zip_code: str, state: str) -> None:
    """ Adds user to users_dict where email is the index. """
    if user_zip_code in ZIP_MAP_DICT:
        users_dict[receiver_email_id] = {'radius': radius,
                                         'user_zip_code': user_zip_code,
                                         'state': state,
                                         'carrier': None,
                                         'usr_prevs_mes': [],
                                         'mes_limit': 150}


def send_message(receiver: str, subject: str, body: str,
                 carrier: Optional[str], carriers_dict: dict) -> None:
    """ Sends mms/email to the user depending on the information they
    provided.
    """
    if carrier is None:
        send_email(receiver, subject, body)
    else:
        send_sms(receiver, subject, body, carrier, carriers_dict)


def update_users_dict(users_dict: dict, start_idx: int) -> int:
    """ Gets information from the google sheets.
    Checks if new users got enrolled.
    Program checks starting from start idx.
    """
    rows = forms.get_spreadsheet_rows()
    row_num = start_idx
    while row_num < len(rows):
        row = rows[row_num]
        if row[1] not in users_dict:
            state = row[1]
            zip_code = row[2]
            radius = int(row[3])
            notif_type = row[4]
        if notif_type == 'Phone':
            phone_num = row[6]
            carrier = row[7]
            add_phone_user(users_dict, phone_num,
                           radius, zip_code, state, carrier)
        else:
            receiver_email = row[5]
            add_email_user(users_dict, receiver_email, radius,
                           zip_code, state)
        row_num += 1
        start_idx = row_num
    return start_idx


def backup_users_dict(users_dict: dict) -> None:
    """ saves user dict in a json file for backup purposes. """
    with open('users.json', 'w') as usrs:
        json.dump(users_dict, usrs)


def backup_int_in_fname(num: int, file_name: str) -> None:
    """ Backups integer in a file """
    with open(file_name, 'w') as fname:
        fname.write(str(num))


def backup_all(users_dict: dict, start_idx: int, num_checked_emails: int)\
        -> None:
    """ Backups users_dict, start_idx and number of checked emails """
    backup_users_dict(users_dict)
    backup_int_in_fname(start_idx, START_IDX_FNAME)
    backup_int_in_fname(num_checked_emails, CHECKED_EMAILS_FNAME)


def do_backup_frequently(start_time: float, users_dict: dict, start_idx: int,
                         num_checked_emails: int) -> float:
    """ The program automatically backups every TIME_BTWN_BACKUPS """
    if (time.time() - start_time) >= TIME_BTWN_BACKUPS:
        backup_all(users_dict, start_idx, num_checked_emails)
        start_time = time.time()
    return start_time


def connected_internet() -> bool:
    """ Checks if program is connected to the internet """
    url = "http://www.google.com"
    timeout = 5
    try:
        requests.get(url, timeout=timeout)
        return True
    except (requests.ConnectionError, requests.Timeout):
        print("\nError: No internet connection!\n")
        return False


def add_to_state_dict(all_states_dict: dict, state: str) -> None:
    """ If a state is not in the all_states_dict, it will retrive
    information of the state from api and add them to the dictionary.
    """
    if state not in all_states_dict:
        url = 'https://www.vaccinespotter.org/api/v0/states/' +\
            f'{state}.json'
        all_states_dict[state] = get_json_dict(url)


def send_message_list(message_lst: list, reciever: str, receiver_data: dict,
                      users_to_remove: list, carriers_dict: dict) -> None:
    """ Sends the message list to the receiver """
    new_prev_mes: list = []
    for message in message_lst:
        if message not in receiver_data['usr_prevs_mes']:
            receiver_data['mes_limit'] -= 1
            send_message(reciever,
                         'New Vaccine Location Detected!',
                         message,
                         receiver_data['carrier'],
                         carriers_dict)
            new_prev_mes.append(message)
    receiver_data['usr_prevs_mes'] = new_prev_mes
    if receiver_data['mes_limit'] <= 0:
        users_to_remove.append(reciever)


def remove_users(users_to_remove: list, users_dict: dict, end_of_service: str,
                 carriers_dict: dict) -> None:
    """ Sends unsubriction messages and updates users_dict accordingly """
    for reciever in users_to_remove:
        if reciever in users_dict:
            send_message(reciever,
                         'Subscription expired',
                         end_of_service,
                         users_dict[reciever]['carrier'],
                         carriers_dict)
            del users_dict[reciever]


def load_dependencies() -> Tuple:
    """ Load the dependency files which are required for program """
    with open('mms_gateways.json') as mms:
        carriers_dict = json.loads(mms.read())
    with open('config.json', 'r') as cfig:
        cfig_dict = json.loads(cfig.read())
    return carriers_dict, cfig_dict


def check_cache(users_dict: dict) -> Tuple:
    """ Check if cache files from previous runs exist.
    If creates creates neww data from scratch.
    """
    try:
        # checks if there are cache file from previous runs
        with open('users.json', 'r') as usrs:
            users_dict_src = json.loads(usrs.read())
        for key in users_dict_src:
            users_dict[key] = users_dict_src[key]
        with open('start_idx.txt', 'r') as idx_file:
            start_idx = int(idx_file.read())
        with open('num_checked_emails.txt', 'r') as emails_num:
            num_checked_emails = int(emails_num.read())
    except FileNotFoundError:
        print('No cache files found.')
        num_checked_emails = 0
        start_idx = update_users_dict(users_dict, 0)
    return start_idx, num_checked_emails


class InputTimedOut(Exception):
    pass


def input_time_out_handler(signum: Any, frame: Any) -> None:
    raise InputTimedOut


def input_with_timeout(timeout: int) -> str:
    unput = ""
    try:
        print(f'You have {timeout} seconds to type in expression. ' +
              'Program will run eval() on what you type. ' +
              'Program execution will continue after you submit command ' +
              'by pressing Enter. If you do not want to evaluate, ' +
              'but want to skip timer, just type skip.\n>>', end='')
        signal.alarm(timeout)
        unput = input()
        signal.alarm(0)
    except InputTimedOut:
        pass
    return unput


def send_vax_messages() -> None:
    """ This fucntion combines everything together.
    Makes sure user doesn
    """
    global SENDER_EMAIL_ID
    global SENDER_EMAIL_ID_PASSWORD
    global ZIP_MAP_DICT
    ZIP_MAP_DICT = create_zip_dict()
    form = ''
    carriers_dict, cfig_dict = load_dependencies()
    SENDER_EMAIL_ID = str(cfig_dict['sender_email_id'])
    SENDER_EMAIL_ID_PASSWORD = str(cfig_dict['sender_email_id_password'])
    form = cfig_dict['form']
    end_of_service = 'This is your last message.\n' +\
        'To contunue receiving messages resubscribe here:\n' +\
        form

    users_dict: dict = {}
    start_idx, num_checked_emails = check_cache(users_dict)
    print('Data from cache or newly created data:\nInitial Users Data:\n' +
          f'{users_dict}\nstart_idx: {start_idx}\n' +
          f'num_checked_emails: {num_checked_emails}\n')

    start_time = time.time()
    previously_disconnected = True
    skip = 'Program will resume.'  # used for user commands.
    runs = 1
    try:
        while True:
            if not connected_internet():
                previously_disconnected = True
                time.sleep(20)
                continue
            if previously_disconnected:
                forms.setup()
                previously_disconnected = False
            print(f'Run number: {runs}')
            start_idx = update_users_dict(
                users_dict, start_idx)
            all_states_dict: dict = {}
            users_to_remove, num_checked_emails =\
                email_read.unsubscribers(num_checked_emails,
                                         SENDER_EMAIL_ID,
                                         SENDER_EMAIL_ID_PASSWORD)
            # receiver either email or phone number
            for reciever in users_dict:
                add_to_state_dict(
                    all_states_dict, users_dict[reciever]['state'])
                message_lst = get_data(users_dict[reciever]['radius'],
                                       users_dict[reciever]['user_zip_code'],
                                       all_states_dict[users_dict[reciever]
                                                       ['state']])
                send_message_list(message_lst, reciever, users_dict[reciever],
                                  users_to_remove, carriers_dict)
            remove_users(users_to_remove, users_dict, end_of_service,
                         carriers_dict)
            print(f'User data after this run:\n{users_dict}\n')
            start_time = do_backup_frequently(start_time, users_dict,
                                              start_idx, num_checked_emails)
            runs += 1
            # allows dev to write one expression.
            signal.signal(signal.SIGALRM, input_time_out_handler)
            uput = input_with_timeout(timeout=REFRESH_PERIOD)
            try:
                print(eval(uput), '\n')
            except Exception as exp:
                if str(exp) != 'unexpected EOF while parsing (<string>, line 0)':
                    backup_all(users_dict, start_idx, num_checked_emails)
                    print(exp, '\n')
                else:
                    print(f'{skip}\n')
    except KeyboardInterrupt:
        print('  Detected KeyboardInterrupt.')
        print('Data has been backed up in cache files.')
        backup_all(users_dict, start_idx, num_checked_emails)


if __name__ == '__main__':
    send_vax_messages()
