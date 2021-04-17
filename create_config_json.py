import json


def main() -> None:
    config_json: dict = {
        'sender_email_id': input('Type the email that will send notifications:\n'),
        'sender_email_id_password': input('password of email:\n'),
        'form': input('URL to the google form:\n'),
        'ss_ID': input('Gooogle sheets spreadsheet id:\n'),
        'SERVICE_ACCOUNT_FILE': input('Google cloud project service account key. ' +
                                      'example output: name_of_file.json\n')
    }

    with open('config.json', 'w') as cfig:
        json.dump(config_json, cfig)
