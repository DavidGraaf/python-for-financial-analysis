# import the necessary packages
import os
from dotenv import load_dotenv
from datetime import date, timedelta
import json
from urllib.request import urlopen
from AdvancedPythonDatabaseModule import sql

# Load the file into memory
load_dotenv('env_vars.env')

# Assign the API key to a variable
database_user = os.getenv('database_user')
database_pass = os.getenv('database_pass')
database_host = os.getenv('database_host')
database_port = os.getenv('database_port')
database_name = os.getenv('database_name')

# Initialize the database connection
db = sql(database_user, database_pass, database_host, database_port, database_name)

# Create a function that loops through the security table and find that latest date in the price table if any
def require_update(security_table):
    # Create dictionary to append data to
    require_update_dict = {
        'securityId': [],
        'ticker': [],
        'from': [],
        'to': []
    }

    # Loop over the security table Id column
    for i in security_table.id:

        # Set today
        today = date.today()

        # Capture the ticker in a variable
        ticker = security_table[security_table['id'] == i]['ticker'].values[0]

        # Use the latest_date_price method of the sql class to determine the latest entry in the database for each security
        recent_date = db.latest_date_price(securityId=i)[0]

        # Logic that checks is the recent date was yesterday or today. If true then skip this portion of the code since no update is necessary.
        if recent_date == (today + timedelta(days=-1)) or recent_date == today:
            continue

        # If most recent date is NOT today or yesterday run the code below
        else:
            # Append the securityId and ticker to the dictionary
            require_update_dict['securityId'].append(i)
            require_update_dict['ticker'].append(ticker)

            # if the recent_date is None, which means there is no entry in the price table for that security then set the "from" and "to" to None
            if recent_date is None:
                require_update_dict['from'].append(None)
                require_update_dict['to'].append(None)
            # If recent_date is NOT None, dynamically populate the "from" and "to" values.
            else:
                recent_dateAddOne = recent_date + timedelta(days=+1)
                require_update_dict['from'].append(recent_dateAddOne.strftime('%Y-%m-%d'))
                require_update_dict['to'].append(today.strftime('%Y-%m-%d'))

    # Returning the populated dictionary
    return require_update_dict

# Define a function that obtains the data and writes it to the database. Function takes a dictionary containing the necessary updates
def obtainData(required_updates):
    # Check if an update is even required, if not print an update to the console
    if len(required_updates['securityId']) == 0:
        print('No update is required, database completely up to date')

    else:
        # save API key to a variable
        api_key = os.getenv('api_key')

        # initialize a dictionary to store the data
        dict_api = {}

        # assign the date the database starts collecting data and today's date to variables
        historic_data_begin = '2005-01-01'
        today = date.today()

        # loop over the length of the dictionary
        for i in range(len(required_updates['securityId'])):
            # Capture the ticker in a variable
            ticker = required_updates['ticker'][i]

            # print statement to write to the console what we are currently doing
            print('Updating:', ticker, '...')

            # Some logic that processes the information in the dictionary and determines the start and end variables
            if required_updates['from'][i] == None:
                start = historic_data_begin
                end = today
            else:
                start = required_updates['from'][i]
                end = required_updates['to'][i]

            # populate the URL for the API pull based on specific security details
            url = "https://financialmodelingprep.com/api/v3/historical-price-full/{}?from={}&to={}&apikey={}".format(
                ticker, start, end, api_key)

            # Capture the response and place in JSON object
            response = urlopen(url)
            data = response.read().decode("utf-8")
            data = json.loads(data)

            # Loop over the JSON and write to the database only if the API actually returned any data
            if len(data) == 0:
                print('Nothing returned from API, perhaps an attempt to retrieve data for a non-market day has been performed.')
                continue
            else:
                for f in data['historical']:
                    insert_statement = """ insert into price ("date", "closingprice", "securityId") values (%s, %s, %s)"""
                    db.queryExec(insert_statement, (f['date'], f['adjClose'], required_updates['securityId'][i],))

                # Print statement to log in console that this ticker is finished updating
                print('Updated ', ticker, 'from: ', start, 'to: ', end)