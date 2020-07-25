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


@app.route("/home/<lang>")
def home(lang):
    return render_template("/home/" + lang + ".html", lang=lang)


@app.route("/clear")
def clear():
    session.clear()
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
        if session == {'_permanent': True} and int(nbr) > 1:  # if session vide
            return redirect("/signup/1/" + lang)
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
            adresseObj = Adresse.find_one(
                {
                    'rue': rue,
                    'ville': ville,
                    'gouvernorat': gouv
                }
            )
            if adresseObj is not None:
                adr_id = adresseObj['_id']
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
        if 'form3' in req:
            adresse2 = req.get('adresse')
            apt_unit2 = req.get('apt_unit')
            adresse = Adresse.find_one({'_id': session['adr_id']})
            joined = ",".join([adresse['rue'], adresse['ville'], adresse['gouvernorat']])
            print(joined)
            if adresse2 != joined or apt_unit2 != Propriete.find_one({'_id': session['apt_id']})['apt_unit']:
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error="l'adresse ou le numero de l'appartement n'est pas le même!")
            city = req.get('city')
            state = req.get('state')
            if city != adresse['ville'] or state != adresse['gouvernorat']:
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error="la ville ou le gouvernorat n'est pas le même!")
            code_postal = req.get('code_postal')
            if code_postal == "":
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error="code postal doit être rempli!")
            Adresse.update_one(
                {'_id': adresse['_id']},
                {"$set": {'code_postal': code_postal}}
            )
            print("code postal added to adresse")
            under_const = req.get('under_construction')
            if under_const == "under_construction":
                Propriete.update_one({'_id': session.get('apt_id')},
                                     {"$set": {'under_construction': True}})
            else:
                Propriete.update_one({'_id': session.get('apt_id')},
                                     {"$set": {'under_construction': False}})
            print(under_const)
        if 'form4' in req:
            rentown = req.get('rentown')
            if rentown is None:
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error="vous devez choisir")
            print(rentown)
            print(session['apt_id'])
            Propriete.update_one({'_id': session['apt_id']},
                                 {"$set": {'rentown': rentown}})
        if 'form5' in req:
            env = req.get('env')
            if env is None:
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error="vous devez choisir")
            print(env)
            if 'alarm' in env:
                Propriete.update_one({'_id': session['apt_id']},
                                     {"$set": {'sys_alarm': True}})
            if 'clim' in env:
                Propriete.update_one({'_id': session['apt_id']},
                                     {"$set": {'climatiseur': True}})
            if 'chauf' in env:
                Propriete.update_one({'_id': session['apt_id']},
                                     {"$set": {'chauffage': True}})

    if session == {'_permanent': True} and int(nbr) > 1:  # if session vide wenti moch fel page 1
        return redirect("/signup/1/" + lang)
    nom = ""
    prenom = ""
    adresse = ""
    apt_unit = ""
    city = ""
    state = ""
    code_postal = ""
    if 'clid' in session:
        pers = Client.find_one({'_id': session['clid']})
        nom = pers['nom']
        prenom = pers['prenom']
        print("client already conneted")
        if 'adr_id' in session:
            adresse1 = Adresse.find_one({'_id': session['adr_id']})
            adresse = ",".join([adresse1['rue'], adresse1['ville'], adresse1['gouvernorat']])
            city = adresse1['ville']
            state = adresse1['gouvernorat']
            if 'code_postal' in adresse1:
                code_postal = adresse1['code_postal']
        if 'apt_id' in session:
            apt_unit = Propriete.find_one({'_id': session['apt_id']})['apt_unit']
    return render_template("signups/signUp" + nbr + ".html",
                           nbr=nbr,
                           lang=lang,
                           nom=nom,
                           prenom=prenom,
                           adresse=adresse,
                           apt_unit=apt_unit,
                           city=city,
                           state=state,
                           code_postal=code_postal
                           )


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
