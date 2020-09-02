import pandas as pd
import pymongo

conc = "mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass%20Community&ssl=false"
client = pymongo.MongoClient(conc)
db = client.cerise_db
def insert_csv(filepath, delimiteur):
    df = pd.read_csv(filepath,encoding = 'ISO-8859-1', delimiter=delimiteur)   # loading csv file
    db['test_adr'].insert_many(df.to_dict('records'))
