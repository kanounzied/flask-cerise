from flask import Flask
# import pymongo
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config['DEBUG'] = True
# conc = "mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass%20Community&ssl=false"
app.config['MONGO_URI'] = "mongodb://localhost:27017/cerise_db"

# client = pymongo.MongoClient(conc)
mongo = PyMongo(app)
# db = client.cerise_db
Admin = mongo.db['Admin']
Client = mongo.db['Client']
Adresse = mongo.db['Adresse']
AutresBiens = mongo.db['AutresBiens']
Categories = mongo.db['Categories']
Contrat = mongo.db['Contrat']
Propriete = mongo.db['Propriete']
collection = mongo.db['constat']