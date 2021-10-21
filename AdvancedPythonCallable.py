# import the necessary packages
import os
from dotenv import load_dotenv
import pandas as pd
from AdvancedPythonDatabaseModule import sql
from AdvancedPythonUtilityModule import require_update, obtainData

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

# Load the security table into memory
security_table = pd.read_sql_table('security', db.connection)

# Call the function to return the tickers that need updating
required_updates = (require_update(security_table))

# Print the dictionary to show the user what data needs to be updated
print(required_updates)

#Call the obtainData function
obtainData(required_updates)

#Query the database to show all the tickers and their most recent date
sql_select_statement = """ select security."ticker" as "ETF Ticker", max(price."date") as "Most Recent Date"
                                from "security"
                                    left join price on "security".id = price."securityId"
                                        group by security."ticker"; """
print(db.queryRetrieve(sql_select_statement, one=False))

#Kill the connection in the database
db.connKiller()