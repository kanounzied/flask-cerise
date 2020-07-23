from ast import dump

from flask import session, render_template, redirect, request
from flask_session import Session
import pymongo
from db_maker import *

app = Flask(__name__)
app.config['DEBUG'] = True
SESSION_TYPE = 'mongodb'
app.config.from_object(__name__)
Session(app)


# Categories.insert_one(
#     {
#         'libelle': "categ_1",
#         'score': 9000
#     }
# )
# print('done')

#    session['key'] = 'value'
#    session.get('key', 'not set')


@app.route("/home/<lang>")
def home(lang):
    return render_template("/home/" + lang + ".html", lang=lang)


@app.route("/clear")
def clear():
    session.clear()
    print(type(Adresse.find_one({"rue": 'taniour'})['proprietes']))
    return "<h1>session cleared"


@app.route("/signup/<nbr>/<lang>", methods=['GET', 'POST'])
def signup(nbr, lang):
    if request.method == "POST":
        req = request.form
        if 'form1' in req:
            prenom = req.get('first_name')
            nom = req.get('last_name')
            if nom == "" or prenom == "":
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error="les champs sont vides")
            client = Client.find_one(
                {
                    'nom': nom,
                    'prenom': prenom
                }
            )
            if client is not None:
                clid = client['_id']
            else:
                clid_ins = Client.insert_one(
                    {
                        'nom': nom,
                        'prenom': prenom
                    }
                )
                clid = clid_ins.inserted_id
            session['clid'] = clid
            print('client created')
        if 'form2' in req:
            adresse = req.get('adresse')
            apt_unit = req.get('apt_unit')
            if adresse == "" or apt_unit == "":
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error="les champs sont vides")

            tab = adresse.split(',')
            if len(tab) != 3:
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error="la forme de l'adresse doit etre comme suit : (rue, ville, gouvernorat)")
            rue = tab[0].strip()
            ville = tab[1].strip()
            gouv = tab[2].strip()
            adresse = Adresse.find_one(
                {
                    'rue': rue,
                    'ville': ville,
                    'gouvernorat': gouv
                }
            )
            if adresse is not None:
                adr_id = adresse['_id']
            else:
                adr_insert = Adresse.insert_one(
                    {
                        'rue': rue,
                        'ville': ville,
                        'gouvernorat': gouv
                    }
                )
                adr_id = adr_insert.inserted_id
            session['adr_id'] = adr_id
            print('adresse created/found')
            apt_id = Propriete.insert_one(
                {
                    "apt_unit": apt_unit,
                    "adr_id": session['adr_id']
                }
            )
            session['apt_id'] = apt_id.inserted_id
            print('apt created')
            adr = Adresse.find_one({'_id': adr_id})
            if 'proprietes' in adr:
                adrtab = adr['proprietes']
                adrtab.append(session.get('apt_id'))
            else:
                adrtab = list([session.get('apt_id')])
            print(adrtab)
            Adresse.update_one(
                {'_id': adr_id},
                {"$set": {'proprietes': adrtab}}
            )
            print('adresse updated')
            contrat = Contrat.insert_one(
                {
                    'client_id': session['clid'],
                    'prop_id': session['apt_id']
                }
            )
            session['cont_id'] = contrat.inserted_id
            print('contrat created')
            client_ = Client.find_one({'_id': session.get('clid')})
            if 'contrats' in client_:
                contab = client_['contrats']
                contab.append(session.get('cont_id'))
            else:
                contab = list([session.get('cont_id')])
            Client.update_one(
                {'_id': session.get('clid')},
                {"$set": {'contrats': contab}}
            )
            print('client updated')
            Propriete.update_one(
                {'_id': session.get('apt_id')},
                {"$set": {'contrat': session.get('cont_id')}}
            )
            print("propriete updated")
    return render_template("signups/signUp" + nbr + ".html", nbr=nbr, lang=lang)


@app.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        print("aaaa")
        req = request.form
        missing = list()

        for k, v in req.items():
            if v == "":
                missing.append(k)

        if missing:
            feedback = f"Missing fields for {', '.join(missing)}"
            return render_template("public/sign_up.html", feedback=feedback, )

        return redirect(request.url)
    return render_template("/public/sign_up.html")


if __name__ == '__main__':
    app.run()

# conc="mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass%20Community&ssl=false"
#
# client = pymongo.MongoClient(conc)
# db = client.test
# collection = db['test']
# collection.insert_one({
#     "_id": 1,
#     "nom": "kanoun",
#     "prenom": "zied"
# })
# print("done")
