installer flask_session
installer mongodb et verifier le port dans db-maker=>conc
pour ecrire les adresses dans un csv execute: python adrCSV.py
pour changer le nom du ficher d'adresses ouvrir adrCSV.py dans la ligne 63 changer le premier champ (adresse.csv)
aller dans mongodb et click sur add data import file csv file avec delimiteur = semicolon et browse
////////
si jamais le serveur mongo refuse la connexion à la base de données aller dans services et activer le !

pou MAGIC

installer 
pip install python-magic-bin==0.4.14
//////////////////////////////////////////
Pour la base de données.

Dans le fchier dbmaker ous trouver le nom de la base
app.config['MONGO_URI'] = "mongodb://localhost:27017/cerise_db2"

create a data base in MongoDB named cerise_db2 and create a collection named Adresse , 
In this collection charge the file in csv format with semicolon seperator.

OK.