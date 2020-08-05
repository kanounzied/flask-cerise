from flask import Flask
import pymongo

app = Flask(__name__)
app.config['DEBUG'] = True
conc = "mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass%20Community&ssl=false"

client = pymongo.MongoClient(conc)
db = client.cerise_db
Admin = db['Admin']
Client = db['Client']
Adresse = db['Adresse']
AutresBiens = db['AutresBiens']
Categories = db['Categories']
Contrat = db['Contrat']
Propriete = db['Propriete']

