# Covid-19 Vaccine Notification

Introduction:
This program sends MMS or Email when a new covid vaccine appointment is found. The website uses the following API https://www.vaccinespotter.org/api/ to get the vaccine availability data.
For a person to subscribe to the covid vaccine updates, they need to fill out a Google Form. The data from the Google Form will be read by the program using the Google Sheets API. To stop receiving messages, it is enought to reply `stop` to the MMS or Email.

We are currently hosting our own implementation of this program. You can subscribe with this Google Form: https://forms.gle/5Gn13Ze8CApHmvNE9. Please note that the program is still a very early beta.

Some questions you can ask our Covid Vaccine Bot are:
- How many total cases are there?
- How many new cases are there?
- Give me the deaths in the US.
- How many new deaths have there been in the US?
- How many people have recovered from COVID in California?
- Give me the number of active cases in San Luis Obispo.
- How many tests have been given in San Jose?


# Setup:
Go to this link https://console.cloud.google.com/home.

Then follow the steps in this YouTube video https://www.youtube.com/watch?v=4ssigWmExak from 3:37 till 9:00.
This YouTube video will guide you on how you will setup the data retrieval from the Google Sheets associated with the Google Form you create; Depending on how you setup the Google Form, the function get_spreadsheet_rows in forms.py will also need some changes in addition to update_users_dict in code.py. However, you can avoid modifying the code if the google sheet has 8 columns. Where the first Row contains these values:

Column 1: Timestamp (Format doesn't matter)

Column 2: State (Should be state abbreviation, all capital letters)

Column 3: Zip Code (Format: XXXXX)

Column 4: Radius (in miles)

Column 5: Receive notifications through (possible values: Email, Phone)

Column 6: Email

Column 7: (Include Area Code) (Format: XXXXXXXXXX)

Column 8: Carrier: (possible values: T-Mobile, Verizon, AT&T)

This is an example of how your Google sheets should look like:
https://docs.google.com/spreadsheets/d/1Gw2s845WRvBz2vbm4fxEHGVf10dnA1nAhaG4MkuoPow/edit?usp=sharing

# Requirements:
To run the program:
Installing Dependencies:
`pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib`


# Steps:
1. Run code.py
2. On your first Run, the program will request the following: the email of the account you will be using to send the SMS/email, the password of that email, the link to the Google Form you are using, the Google Sheet Spreadsheet ID, and the service key (the json file created after watching the YouTube video). Note: A config.json file will be created according to the values you enter.
3. After that the program will run. The program will continuously check the results of the Google Form and the Vaccine Spotter API. If the program is exited using KeyboardInterupt (ctrl + c), it will automatically save the state at which it stopped at in the files users.json, start_idx.txt, and num_checked_emails.txt. If you want to modify the Google Sheet, you need to stop program execution and delete the users.json, start_idx.txt, and num_checked_emails.txt files. Please note that the only way you should modify the Google Sheet is by deleting entries (fully delete the row in the Google Sheet).
