#import the create_engine method from sqlalchemy package
from sqlalchemy import create_engine

# Create a sql class that takes care of all things related to the database
class sql:
    def __init__(self, user, password, host, port, name):
        # Create an engine
        self.engine = create_engine(
            'postgresql+psycopg2://{0}:{1}@{2}:{3}/{4}'.format(user, password, host, port, name))
        # Create a connection
        self.connection = self.engine.connect()

    # method for query execution. This can for example be used to insert and create tables
    def queryExec(self, query, *data):
        self.connection.execute(query, *data)

    # query retrieve function. If one argument is set to True it only returns one row of the database if set to False it will retrieve all
    def queryRetrieve(self, query, one=False):
        if one == False:
            return self.connection.execute(query).fetchall()
        else:
            return self.connection.execute(query).fetchone()

    def latest_date_price(self, securityId):
        query = """ select max(date) from price where price."securityId" = {0}""".format(securityId)
        return self.queryRetrieve(query, one=True)

    # Close the connection
    def connKiller(self):
        self.connection.close()