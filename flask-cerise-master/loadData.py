import binascii, hashlib, os
import datetime

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
    # block pour lier tous les appartements dans l même adresse
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
