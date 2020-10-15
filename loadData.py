import binascii, hashlib, os
import datetime
import math
from db_maker import *


def hash_password(password):
    """Hash a password for storing."""
    # salt1 = b'2\xec\x80\x9b\x8f\xa4\x19xuM\xc3g\xf6\x1a\xeb\xee\x8cK\x99\x18_\x93R\xe5\xf8\n\xaa%T\x12\x07\x04c\xb3-\x9b=\xf0!\x16-\x03y\xaa\x92\xf5\xb6\xb4\xe09\x08\xbd\xc2\xf0\xa6J\xbe\x9e\xd8\xd1'
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                  salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')


def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                  provided_password.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password


def load(client, propriete, adresse):
    dbclient = Client.find_one({
        'email': client['email'],
    })
    if dbclient is None:
        client = Client.insert_one({
            'prenom': client['prenom'],
            'nom': client['nom'],
            'email': client['email'],
            'cin': client['cin'],
            'tel_num': client['tel_num'],
            'date_de_naissance': client['date_de_naissance'],
            'adresse': client['adresse'],
            'type_famille': client['type_famille'],
            'password': client['password'],
            'confirmed': client['confirmed']
        })
        clid = client.inserted_id
    else:
        client = dbclient
        clid = client['_id']

    client = Client.find_one({'_id': clid})
    adr_id = Adresse.find_one({'adresse': adresse})['_id']
    prop = Propriete.insert_one({
        'apt_unit': propriete['apt_unit'],
        'nbr_chambres': propriete['nbr_chambres'],
        'rentown': propriete['rentown'],
        'etage': propriete['etage'],
        'sys_alarm': propriete['sys_alarm'],
        'climatisation': propriete['climatisation'],
        'chauffage': propriete['chauffage'],
        'type': propriete['type'],
        'surface': propriete['surface'],
        'jardin': propriete['under_construction'],
        'rue': propriete['rue'],
        'valuables': propriete['valuables'],
        'under_construction': propriete['under_construction'],
        'adr_id': adr_id
    })
    propid = prop.inserted_id
    from cerise_inst import session
    session['apt_id'] = propid
    session['clid'] = clid
    x = datetime.datetime.now()
    # print(x.strftime("%d" + "/" + "%m" + "/" + "%Y"))
    contrat = Contrat.insert_one(
        {'client_id': clid, 'prop_id': propid, 'date_debut': x.strftime("%d" + "/" + "%m" + "/" + "%Y")})
    # print('contract created')
    session['cont_id'] = contrat.inserted_id
    Propriete.update_one({'_id': propid}, {'$set': {'contrat': contrat.inserted_id}})
    # print('property updated')
    if 'contrats' in client:  # ajouter un contrat
        contab = client['contrats']
        contab.append(contrat.inserted_id)
    else:
        contab = list([contrat.inserted_id])  # creer un contrat
    Client.update_one(
        {'_id': clid},
        {"$set": {'contrats': contab}}
    )
    # print('client updated')
    adr = Adresse.find_one({'_id': adr_id})
    # block pour lier tous les appartements dans l m�me adresse
    if 'proprietes' in adr:
        adrtab = adr['proprietes']
        adrtab.append(propid)
    else:
        adrtab = list([propid])
    Adresse.update_one(
        {'_id': adr_id},
        {"$set": {'proprietes': adrtab}}
    )
    # print('address updated')
    if 'coverage' not in Contrat.find_one({'_id': contrat.inserted_id}):
        for str in ['propriete_personnelle', 'obligation_personnelle', 'payement_medical', 'perte_usage']:
            tab = list([])
            contrat2 = Contrat.find_one({'_id': contrat.inserted_id})
            # print(str)
            if 'coverage' not in contrat2:
                # print('contrat2')
                Contrat.update_one(
                    {'_id': contrat.inserted_id},
                    {'$set': {'coverage': tab}}
                )
            else:
                tab = contrat2['coverage']
                # print(tab)
            price = 200
            if str == 'propriete_personnelle': price = 500
            if str == 'payement_medical': price = 100
            if str == 'perte_usage': price = 500
            tab.append({
                'libelle': str,
                'valeurEstimee': price
            })
            Contrat.update_one(
                {'_id': contrat.inserted_id},
                {'$set': {'coverage': tab}}
            )
    if 'autres_biens' not in Propriete.find_one({'_id': propid}):
        for str in ['bijoux', 'beaux_arts', 'velos', 'cameras', 'instruments_de_musique']:
            id = AutresBiens.insert_one({
                'libelle': str,
                'valeurEstimee': 200,
                'propriete_id': propid
            })
            id = id.inserted_id
            tab = list([])
            prop = Propriete.find_one({'_id': propid})
            if 'autres_biens' not in prop:
                Propriete.update_one(
                    {'_id': propid },
                    {'$set': {'autres_biens': tab}}
                )
            else:
                tab = prop['autres_biens']
            tab.append(id)
            Propriete.update_one(
                {'_id': propid},
                {'$set': {'autres_biens': tab}}
            )
    if 'deductible' not in Contrat.find_one({'_id': contrat.inserted_id}):
        Contrat.update_one({'_id': contrat.inserted_id}, {'$set': {'deductible': 250}})


def loadAuto(client, voiture, garantie):
    dbclient = Client.find_one({
        'email': client['email'],
    })
    from cerise_inst import session
    if dbclient is None:
        client = Client.insert_one({
                'prenom': session.get('client')['prenom'],
                'nom': session.get('client')['nom'],
                'email': session.get('client')['email'],
                'cin': session.get('client')['cin'],
                'tel': session.get('client')['tel_num'],
                'date_de_naissance': session.get('client')['date_de_naissance'],
                'adresse': session.get('client')['adresse'],
                'password': session.get('client')['password'],
                'confirmed': session.get('client')['confirmed']
                 
            })
        client_id = client.inserted_id
    else: 
        client = dbclient
        client_id = client['_id']

    client = Client.find_one({'_id': client_id})

    voiture = Voiture.insert_one({
                'client_id': client_id,
                'type': session.get('voiture')['typev'],
                'marq_model': session.get('voiture')['marq_model'],
                'matricule': session.get('voiture')['matricule'],
                'puissance_fiscale': session.get('voiture')['puissance'],
                'valeur_a_neuf': session.get('voiture')['valeur_a_neuf'],
                'valeur_actuelle': session.get('voiture')['valeur_actuelle'],
                'bonus_malus': session.get('voiture')['bonus_malus']
                    })

    void = voiture.inserted_id

    garantie = Garantie.insert_one({
            
                'client_id': client_id,
                'voiture_id': void,
                'incendie-vol': session.get('garantie')['incendie'],
                'dommage_collision': session.get('garantie')['dommage_collision'],
                'dommage_tous_risques': session.get('garantie')['dommage_tous_risques'],
                'franchise_TR': session.get('garantie')['franchise'],
                'radio_cassette': session.get('garantie')['valeur_rc'],
                'bris_de_glace': session.get('garantie')['valeur_bg'],
                'remorquage': session.get('garantie')['remorquage'],
                'nbr_pers_transporte': session.get('garantie')['nbp'],
                'capital_deces': session.get('garantie')['capital_d'],
                'conducteur_plus': session.get('garantie')['conducteur_plus'],
                'capital_assure_cp': session.get('garantie')['capital_assure_cp']
            })

    garid = garantie.inserted_id
    session['garid'] = garid
    session['client_id'] = client_id
    session['void'] = void
    x = datetime.datetime.now()

    contratv = Contrat_voiture.insert_one(
        {'client_id': client_id,
         'garantie_id': garid,
         'date_de_debut_du_contrat': x.strftime("%d" + "/" + "%m" + "/" + "%Y") }
    )
    session['contv_id'] = contratv.inserted_id
    Garantie.update_one({'_id': garid}, {'$set': {'contract': contratv.inserted_id}})
    session.get('garantie')['contract'] = contratv.inserted_id
    if 'contratsV' in client:
        contab = client['contratsV']
        contab.append(contratv.inserted_id)
    else : 
        contab = list([contratv.inserted_id])
    Client.update_one({'_id': client_id}, {'$set': {'contratsV': contab}})
    voit = Voiture.find_one({'_id': void})
    if 'garanties' in voit :
        voitab = voit['garanties']
        voitab.append(garid)
    else:
        voitab = list([garid])
    Voiture.update_one({'_id': void}, {'$set': {'garanties': voitab}}) 

    list_garantie = [['Incendie/Vol' , Garantie.find_one({'_id': garid})['incendie-vol']],
        ['Dommage Collision', Garantie.find_one({'_id': garid})['dommage_collision']],
        ['Dommage Tous Risques', Garantie.find_one({'_id': garid})['dommage_tous_risques']],
        ['Franchise Dommage Tous Risque', Garantie.find_one({'_id': garid})['franchise_TR']],
        ['Radio Cassette', Garantie.find_one({'_id': garid})['radio_cassette']],
        ['Bris de Glace', Garantie.find_one({'_id': garid})['bris_de_glace']],  
        ['Remorquage', Garantie.find_one({'_id': garid})['remorquage']],
        ['Nombre de personnes transportees', Garantie.find_one({'_id': garid})['nbr_pers_transporte']],
        ['Capital Deces', Garantie.find_one({'_id': garid})['capital_deces']],
        ['Conducteur Plus', Garantie.find_one({'_id': garid})['conducteur_plus']],
        ['Capital Assure conducteurplus', Garantie.find_one({'_id': garid})['capital_assure_cp']]]

    tab = list([])

    Contrat_voiture.update_one(
        {'_id': contratv.inserted_id},
        {'$set': {'coveragev': tab}}
    )
    year_price = 0

    for val in list_garantie : 

        price = 0

        if val[0] == "Incendie/Vol":
            price= int(val[1])*0.005
    
        elif val[0] == "Dommage Collision" and val[1] != "EXCLUE":
            price= int(val[1])*0.1

        elif val[0] == "Dommage Tous Risque" and val[1] != "EXCLUE":
            price= int(val[1])*0.02453
        elif val[0] == "Radio Cassette" and val[1]!="EXCLUE":
            price= int(val[1])*0.07
        elif val[0] == "Bris de Glace" and val[1]!="EXCLUE":
            price= int(val[1])*0.07   
        elif val[0] == "Capital Deces" and val[1] != "EXCLUE":
            price = int(val[1])*0.0016
        elif val[0] == "Capital Assure conducteurplus" and val[1] != "EXCLUE":
            price= int(val[1])*0.001
        
        year_price += round(price, 1)
        tab.append({
            'libelle': val[0],
            'valeur': val[1],
            'valeurEstimee': round(price, 1)
        })
        Contrat_voiture.update_one(
                {'_id': contratv.inserted_id},
                {'$set': {'coveragev': tab}}
            )
    
    month_price = round(year_price/12, 1)
    year_discount = round((year_price*5)/100, 1)
    print(year_price)
    print(month_price)
    print(year_discount)
    session['price_voiture'] = {
        'year_price': round(year_price - year_discount, 1),
        'month_price': round(month_price, 1)
    }
    if 'year_price' not in Contrat_voiture.find_one({'_id': contratv.inserted_id}):
        Contrat_voiture.update_one({'_id': contratv.inserted_id}, {'$set': {'year_price': year_price}})
    if 'year_discount' not in Contrat_voiture.find_one({'_id': contratv.inserted_id}):
        Contrat_voiture.update_one({'_id': contratv.inserted_id}, {'$set': {'year_discount': year_discount}})
    if 'month_price' not in Contrat_voiture.find_one({'_id': contratv.inserted_id}):
        Contrat_voiture.update_one({'_id': contratv.inserted_id}, {'$set': {'month_price': month_price}})
