from flask import session, render_template, redirect, request
from flask_session import Session

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
            data = list([])
            cursor = Adresse.find({})
            for doc in cursor:
                data.append(doc['adresse'])
            if adresse == "" or apt_unit == "":
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       data=data,
                                       error="les champs sont vides")

            tab = adresse.split(',')
            if len(tab) != 3:
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       data=data,
                                       error="la forme de l'adresse doit etre comme suit : (rue, ville, gouvernorat)")
            rue = tab[0].strip()
            ville = tab[1].strip()
            gouv = tab[2].strip()
            adresseObj = Adresse.find_one(
                {
                    'adresse': adresse
                }
            )
            if adresseObj is None:
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       data=data,
                                       error="Votre adresse n'est pas enregistrée dans la base de données!")
            print(adresseObj)
            adr_id = adresseObj['_id']
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
            print(adresse['adresse'], adresse2)
            if adresse2 != adresse['adresse'] or apt_unit2 != Propriete.find_one({'_id': session['apt_id']})[
                'apt_unit']:
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       adresse=adresse['adresse'],
                                       error="l'adresse ou le numero de l'appartement n'est pas le même!")
            city = req.get('city')
            state = req.get('state')
            tab = adresse2.split(',')
            print(tab)
            if city.strip() != tab[1].strip() or state.strip() != tab[0].strip():
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error="la ville ou le gouvernorat n'est pas le même!")
            code_postal = req.get('code_postal')
            if code_postal == "":
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error="code postal doit être rempli!")
            if code_postal != Adresse.find_one({'_id': adresse['_id']})['code_postal']:
                codes = Adresse.find({'code_postal': code_postal})
                code_postal = list([])
                for code in codes:
                    code_postal.append(code['adresse']+" :"+str(code['code_postal']))
                print(code_postal)
                adresse1 = Adresse.find_one({'_id': session['adr_id']})
                adresse = adresse1['adresse']
                tab = adresse.split(',')
                city = tab[1]
                state = tab[0]
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       code=code_postal,
                                       alrt=True,
                                       city=city,
                                       state=state,
                                       )
            print("code postal verifié")
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
            if (rentown not in ['own', 'rent', None]):
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error="bien joué lol!")
            Propriete.update_one({'_id': session['apt_id']},
                                 {"$set": {'rentown': rentown}})
        if 'form5' in req:
            env1 = req.get('alarm')
            env2 = req.get('clim')
            env3 = req.get('chauf')
            if (env1 not in ['alarm', None]) or (env2 not in ['clim', None]) or (env3 not in ['chauf', None]):
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error="hacker wallah!!")
            if env1 == "alarm":
                Propriete.update_one({'_id': session['apt_id']},
                                     {"$set": {'sys_alarm': True}})
            elif env1 is None:
                Propriete.update_one({'_id': session['apt_id']},
                                     {"$set": {'sys_alarm': False}})
            if env2 == 'clim':
                Propriete.update_one({'_id': session['apt_id']},
                                     {"$set": {'climatiseur': True}})
            elif env2 is None:
                Propriete.update_one({'_id': session['apt_id']},
                                     {"$set": {'climatiseur': False}})
            if env3 == 'chauf':
                Propriete.update_one({'_id': session['apt_id']},
                                     {"$set": {'chauffage': True}})
            elif env3 is None:
                Propriete.update_one({'_id': session['apt_id']},
                                     {"$set": {'chauffage': False}})
        if 'form6' in req:
            type_ = req.get('type')
            if type_ not in ['maison', 'villa', 'appartement', None]:
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error="al3ab b3id!")
            if type_ is None:
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error="vous devez choisir!")
            Propriete.update_one({'_id': session['apt_id']},
                                 {"$set": {'type': type_}})
        if 'form7' in req:
            room = req.get('room')
            etage = req.get('etage')
            if (int(room) not in list(range(50))) or (int(etage) not in list(range(100))):
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error="vous devez choisir un entier positif")
            Propriete.update_one({'_id': session['apt_id']},
                                 {"$set": {'nbr_chambres': room}})
            Propriete.update_one({'_id': session['apt_id']},
                                 {"$set": {'etage': etage}})
        if 'form8' in req:
            garden = req.get('garden')
            pool = req.get('pool')
            if (garden not in ['garden', None]) or (pool not in ['pool', None]):
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error="stop changing values!")
            if garden == 'garden':
                Propriete.update_one({'_id': session['apt_id']},
                                     {"$set": {'garden': True}})
            else:
                Propriete.update_one({'_id': session['apt_id']},
                                     {"$set": {'garden': False}})
            if pool == 'pool':
                Propriete.update_one({'_id': session['apt_id']},
                                     {"$set": {'pool': True}})
            else:
                Propriete.update_one({'_id': session['apt_id']},
                                     {"$set": {'pool': False}})
        if 'form9' in req:
            surface = req.get('range')
            if surface is None:
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error="you must choose a range!")

    if session == {'_permanent': True} and int(nbr) > 1:  # if session vide wenti moch fel page 1
        return redirect("/signup/1/" + lang)
    nom = ""
    prenom = ""
    adresse = ""
    apt_unit = ""
    city = ""
    state = ""
    code_postal = ""
    data = list([])
    if 'clid' in session:
        pers = Client.find_one({'_id': session['clid']})
        nom = pers['nom']
        prenom = pers['prenom']
        print("client already conneted")
        if 'adr_id' in session:
            adresse1 = Adresse.find_one({'_id': session['adr_id']})
            adresse = adresse1['adresse']
            tab = adresse.split(',')
            city = tab[1]
            state = tab[0]
            code_postal = adresse1['code_postal']
        if 'apt_id' in session:
            apt_unit = Propriete.find_one({'_id': session['apt_id']})['apt_unit']
    cursor = Adresse.find({})
    for doc in cursor:
        data.append(doc['adresse'])
    return render_template("signups/signUp" + nbr + ".html",
                           nbr=nbr,
                           lang=lang,
                           nom=nom,
                           prenom=prenom,
                           adresse=adresse,
                           apt_unit=apt_unit,
                           city=city,
                           state=state,
                           code_postal=code_postal,
                           data=data
                           )


if __name__ == '__main__':
    app.run()
