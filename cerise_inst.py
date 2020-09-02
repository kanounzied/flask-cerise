import base64
import datetime
import random
import pdfkit

from datetime import timedelta

from flask import session, render_template, redirect, request, jsonify, url_for, abort, make_response
from flask_assets import Environment, Bundle
from flask_recaptcha import ReCaptcha
from flask_session import Session
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature

from classes import *
from db_maker import *
from loadData import load, hash_password, verify_password
from sendMail import *

app = Flask(__name__)
recaptcha = ReCaptcha(app=app)
app.config['DEBUG'] = True
app.config['SECURITY_PASSWORD_SALT'] = 'my_security_salt'
app.config['RECAPTCHA_ENABLED'] = True
app.config['RECAPTCHA_SITE_KEY'] = "6LfBg8MZAAAAANGW1yEb9v12b-qbpmMvgSmOd_Tj"
app.config['RECAPTCHA_SECRET_KEY'] = "6LfBg8MZAAAAAPpVBz2VrTYu2faszGQxroVUrhfH"
recaptcha = ReCaptcha()
recaptcha.init_app(app)
app.config['SECRET_KEY'] = 'djeja'
SESSION_TYPE = 'mongodb'
app.config.from_object(__name__)
assets = Environment(app)
assets.url = app.static_url_path
assets.debug = True
scss = Bundle('styles/stylesheet2.scss', filters='pyscss', output='gen/all.css')
assets.register('scss_all', scss)
Session(app)
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])


@app.before_request
def make_session_permanent():  # la session est valide pour seulement une heure
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=60)


@app.route("/")
def arab():
    return redirect("/home/arabe")

@app.route("/home/<lang>")
def home(lang):
    return render_template("/home/" + lang + ".html", lang=lang)


@app.route("/clear")
def clear():  # vider la session client
    session.clear()
    return "<h1>session cleared"


@app.route("/signup/<nbr>/<lang>", methods=['GET', 'POST'])
def signup(nbr, lang):
    # if 'finished' in session:
    #     return redirect('/preview/' + lang)
    # block des erreurs en trois langues
    if lang == 'french':
        champerr = 'les champs sont vides!'
        adresserr = "la forme de l'adresse doit etre comme suit : (localité, délégation, gouvernorat)"
        adrnotfound = "Votre adresse n'est pas enregistrée dans la base de données!"
        chooseerr = "vous devez choisir!"
        rangeerr = "vous devez choisir un entier entre 1 et 30 pour les chambres et 50 pour les étages!"
        pwderr = "votre mot de passe n'est pas le méme!"
        pwdregex = "mot de passe doit avoir une lettre miniscule, une lettre majuscule, un chiffre, et l'un des charactéres suivants @#$%^&+= "
        verify = "Nous vous avons envoyé un mail pour confirmer votre adresse email !"
        emailexisterr = "Cet email est déja dans la base de données veuillez saisir un autre email!"
    elif lang == 'english':
        champerr = 'fields are empty!'
        adresserr = "address form must be like : (locality, delegation, governorate)"
        adrnotfound = "Your address is not registered in the database!"
        chooseerr = "you must choose!"
        rangeerr = "you must choose a number in range 1 to 30 rooms or to 50 floors!"
        pwderr = "your password doesn't match!"
        pwdregex = "your password must have a miniscule letter, a capital letter, a number, and one of the following characters @#$%^&+="
        verify = "We've sent you a verification mail for your email address !"
        emailexisterr = "This email is already in data base please type another email!"
    else:
        champerr = 'البلايص فارغين'
        adresserr = "لازم الادريسة هكا : (محافظه، وفد، منطقه)"
        adrnotfound = "عنوانك غير مسجل في قاعدة البيانات!"
        chooseerr = "لازم تختار!"
        rangeerr = "لازم تختار عدد بين 1 و 30 بيت أو 50 طابق!"
        pwderr = "كلمة المرور الخاصة بك لا تتطابق!"
        pwdregex = "يجب أن تحتوي كلمة المرور على الأقل على حرف صغير[a .. z]، حرف كبير[A .. Z]، رقم، واحد من الرموز التالية @#$%^&+="
        verify = "!لقد أرسلنا لك بريد التحقق من عنوان البريد الإلكتروني الخاص بك"
        emailexisterr = "!هذا البريد الإلكتروني موجود في قاعدة البيانات، الرجاء كتابة بريد إلكتروني آخر"
    if request.method == "POST":
        req = request.form
        if 'form1' in req:
            prenom = req.get('first_name')
            nom = req.get('last_name')
            if nom == "" or prenom == "":
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=champerr)
            client = Client_(prenom, nom)
            session['client'] = client.__dict__
            print('client created')
            session['form1'] = 'submitted'
        if 'form1' not in session:
            return redirect('/signup/1/' + lang)
        if 'form2' in req:
            adresse = req.get('adresse')
            apt_unit = req.get('apt_unit')
            data = list([])
            cursor = Adresse.find({})
            for doc in cursor:  # préparer les adresses de la bd pour la template
                data.append(doc['adresse'])
            if adresse == "" or apt_unit == "":
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       data=data,
                                       error=champerr)

            tab = adresse.split(',')
            alladdres = Adresse.find({})
            if len(tab) != 3:
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       data=data,
                                       error=adresserr)
            # rue = tab[0].strip()
            # ville = tab[1].strip()
            # gouv = tab[2].strip()
            adresseObj = Adresse.find_one(
                {
                    'adresse': adresse
                }
            )
            if adresseObj is None:
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       data=data,
                                       error=adrnotfound)
            print(adresseObj)
            adr_id = adresseObj['_id']
            session['adr_id'] = adr_id
            print('adresse found')
            # apt_id = Propriete.insert_one(  # inserer la classe propriété dans bd
            #     {
            #         "apt_unit": apt_unit,
            #         "adr_id": session['adr_id']
            #     }
            # )
            apt = Propriete_(apt_unit)
            apt.jardin = True
            session['apt'] = apt.__dict__
            print('apt created')
            session['form2'] = 'submitted'
        if 'form3' in req:
            adresse = Adresse.find_one({'_id': session['adr_id']})
            apt = session.get('apt')
            print(adresse['adresse'])
            under_const = req.get('under_construction')
            if under_const == "under_construction":
                apt['under_construction'] = True
            else:
                apt['under_construction'] = False
            rue = req.get('adresse')
            if rue == "":
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=champerr)
            if session['apt'] is not None:
                apt['rue'] = rue
            session['form3'] = 'submitted'
        if 'form4' in req:
            rentown = req.get('rentown')
            if rentown is None:
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=chooseerr)
            if rentown not in ['own', 'rent', None]:
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error="please do not change values!")
            session['apt']['rentown'] = rentown
            session['form4'] = 'submitted'
        if 'form5' in req:
            env1 = req.get('alarm')
            env2 = req.get('clim')
            env3 = req.get('chauf')
            if (env1 not in ['alarm', None]) or (env2 not in ['clim', None]) or (env3 not in ['chauf', None]):
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error="please do not change values!")
            if env1 == "alarm":
                session.get('apt')['sys_alarm'] = True
            elif env1 is None:
                session.get('apt')['sys_alarm'] = False
            if env2 == 'clim':
                session.get('apt')['climatisation'] = True
            elif env2 is None:
                session.get('apt')['climatisation'] = False
            if env3 == 'chauf':
                session.get('apt')['chauffage'] = True
            elif env3 is None:
                session.get('apt')['chauffage'] = False
            session['form5'] = 'submitted'
        if 'form6' in req:
            type_ = req.get('type')
            if type_ not in ['maison', 'villa', 'appartement', None]:
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error="please do not change values!")
            if type_ is None:
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=chooseerr)
            session['apt']['type'] = type_
            session['form6'] = 'submitted'
        if 'form7' in req:
            room = req.get('room')
            etage = req.get('etage')
            if (int(room) not in list(range(30))) or (int(etage) not in list(range(100))):
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=rangeerr)
            session.get('apt')['nbr_chambres'] = room
            session.get('apt')['etage'] = etage
            # Propriete.update_one({'_id': session['apt_id']},
            #                      {"$set": {'nbr_chambres': room}})
            # Propriete.update_one({'_id': session['apt_id']},
            #                      {"$set": {'etage': etage}})
            session['form7'] = 'submitted'
        if 'form8' in req:
            garden = req.get('garden')
            pool = req.get('pool')
            if (garden not in ['garden', None]) or (pool not in ['pool', None]):
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error="please do not change values!")
            apt = session.get('apt')
            if garden == 'garden':
                apt['jardin'] = True
                # Propriete.update_one({'_id': session['apt_id']},
                #                      {"$set": {'garden': True}})
            else:
                apt['jardin'] = False
                # Propriete.update_one({'_id': session['apt_id']},
                #                      {"$set": {'garden': False}})
            if pool == 'pool':
                apt['pool'] = True
                # Propriete.update_one({'_id': session['apt_id']},
                #                      {"$set": {'pool': True}})
            else:
                apt['pool'] = False
                # Propriete.update_one({'_id': session['apt_id']},
                #                      {"$set": {'pool': False}})
            session['form8'] = 'submitted'
        if 'form9' in req:
            surface = req.get('range')
            if surface is None:
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=chooseerr)
            session.get('apt')['surface'] = surface
            # Propriete.update_one({'_id': session.get('apt_id')}, {'$set': {'surface': surface}})
            session['form9'] = 'submitted'
        if 'form10' in req:
            # client type_famille
            famtype = req.get('family')
            if famtype not in ['single', 'couple', 'family', 'single_parent', 'other', None]:
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error="don't change values please!")
            if famtype is None:
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=chooseerr)
            session.get('client')['type_famille'] = famtype
            session['form10'] = 'submitted'
        if 'form11' in req:
            yn = req.get('valuables')
            if yn not in ['yes', 'no', None]:
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error="don't change values please!")
            if yn == None:
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=chooseerr)
            session.get('apt')['valuables'] = yn
            # Propriete.update_one({'_id': session['apt_id']}, {'$set': {'valuables': yn}})
            session['form11'] = 'submitted'
        if 'form12' in req:
            email = req.get('email')
            if email == "":
                print(email, 'none ')
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=champerr)
            session.get('client')['email'] = email
            client = session.get('client')
            if Client.find_one({'email': client['email']}):  # client already in data base
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=emailexisterr)
            token = s.dumps(email, salt='email-confirm')
            link = url_for('confirm_email', lang=lang, token=token, _external=True)
            sendConfirm(email, link)
            session['form12'] = 'submitted'
            return render_template('confirm/confirm.html', confirmed=False, error=verify, lang=lang)
        if 'form13' in req:
            pwd = req.get('password')
            cpwd = req.get('confirm-password')
            if pwd != cpwd:
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=pwderr)
            import re
            pattern = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
            password = pwd
            result = re.findall(pattern, password)
            if not result:
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=pwdregex)
            session.get('client')['password'] = hash_password(pwd)
            session['form13'] = 'submitted'
        if 'form14' in req:
            tel = req.get('tel')
            cin = req.get('cin')
            birth = req.get('birth')
            if birth == "" or tel == "" or cin == "":
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=champerr)
            session.get('client')['date_de_naissance'] = birth
            session.get('client')['tel_num'] = tel
            session.get('client')['cin'] = cin
            session['form14'] = 'submitted'
    if session == {'_permanent': True} and int(nbr) > 1:  # if session vide wenti moch fel page 1
        return redirect("/signup/1/" + lang)

    if int(nbr) in range(2, 15) and ('form' + str(int(nbr) - 1) not in session):
        form = ""
        for i in range(2, 15):
            if ('form' + str(i)) in session:
                form = str(i - 1)
        return redirect("/signup/" + form + "/" + lang)
    nom = ""
    prenom = ""
    adresse = ""
    apt_unit = ""
    city = ""
    state = ""
    code_postal = ""
    data = list([])
    email = ""
    rue = ""
    if 'client' in session:
        pers = session.get('client')
        nom = pers['nom']
        prenom = pers['prenom']
        if 'email' in pers:
            email = pers['email']
        print("client already conneted")
        if 'adr_id' in session:
            adresse1 = Adresse.find_one({'_id': session['adr_id']})
            adresse = adresse1['adresse']
            tab = adresse.split(',')
            city = tab[1]
            state = tab[0]
            code_postal = adresse1['code_postal']
        if 'apt' in session:
            apt_unit = session.get('apt')['apt_unit']
    cursor = Adresse.find({})
    for doc in cursor:
        data.append(doc['adresse'])
    if nbr == "15" and request.method == 'POST':
        if session.get('client')['confirmed']:
            propriete = session.get('apt')
            client = session.get('client')
            load(client, propriete, adresse)
            session['loaded'] = True
            session['done'] = True
            session['finished'] = True  # finished is for when the client submits the last form (passwords) and from
                                        # then he shouldn't be allowed to return to signups
            text_association = "this is the contract of the client : "+client['nom']+' '+client['prenom']+" with the id "\
                   +str(session.get('clid'))+" : <br>this contract is still not paid"
            sendPDF('zied.kanoun6@gmail.com', 'demande_de_stage.pdf', text_association)
            text_client = "the contract is ready now and waiting to be paid!<br> if you want to modify it just log in and choose" \
                          " your contract if you have more than one"
            sendPDF(client['email'], 'demande_de_stage.pdf', text_client)
            return redirect("/preview/" + lang)
    elif nbr == "15" and request.method == 'GET':
        abort(403)
    jump = False
    if nbr == "8" and session.get('apt')['type'] == 'appartement':
        nbr = "9"
        jump = True
        session.get('apt')['jardin'] = False
        session.get('apt')['pool'] = False
    if int(nbr) > 12 and session.get('client')['confirmed'] == False:
        return render_template('confirm/confirm.html', confirmed=False, error=verify, lang=lang)
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
                           data=data,
                           email=email,
                           jump=jump
                           )


@app.route("/preview/<lang>", defaults={'index': '0'})
@app.route("/preview/<lang>/<index>")
def preview(lang, index):
    if index != '0':
        client = session.get('client')
        contrat = client['contrats'][int(index) - 1]
        contrat = Contrat.find_one({'_id': contrat})
        apt = Propriete.find_one({'_id': contrat['prop_id']})
        session['apt_id'] = apt['_id']
        session['apt'] = apt
        session['contrat'] = contrat
        session['adr_id'] = apt['adr_id']
    if session.get('adr_id') != 'multiple':
        adresse = Adresse.find_one({'_id': session.get('adr_id')})['adresse']
        apt = session.get('apt')
        rue = apt['rue']
        apt_unit = apt['apt_unit']
        done = False  # pour afficher la page de preload
        jeweler = False  # pour afficher la partie extra coverage
        if apt['valuables'] == 'yes':
            jeweler = True
        if 'done' in session:
            done = True
        client = session.get('client')
        propriete = session.get('apt')
        if 'loaded' not in session:
            load(client, propriete, adresse)
            session['loaded'] = True
        adresse = apt_unit + "," + rue + ", " + adresse  # careful
        return render_template("resultat/preview.html",
                               lang=lang,
                               done=done,
                               adresse=adresse,
                               valuables=jeweler,
                               )
    else:
        client = session.get('client')
        proprietes = list([])
        for cont in client['contrats']:
            cnt = Contrat.find_one({'_id': cont})
            apt = Propriete.find_one({'_id': cnt['prop_id']})
            adresse = Adresse.find_one({'_id': apt['adr_id']})['adresse']
            proprietes.append('adresse : ' + apt['apt_unit'] + ", " + apt['rue'] + "  " + adresse)
        return render_template("resultat/multiple.html", contrats=proprietes, lang=lang)

@app.route('/print/session')
def printsess():
    return session.__dict__


@app.route("/login/<lang>", methods=['POST', 'GET'])
def login(lang):
    pwderror = ''
    mailerr = ''
    error = ''
    if lang == 'french':
        pwderror = 'Verifiez votre mot de passe !'
        mailerr = 'Verifiez votre email !'
        recaptchaerr = "Veuillez confirmer que vous n'êtes pas un robot!"
    if lang == 'english':
        pwderror = 'Verify your password ! '
        mailerr = 'Verify your email !'
        recaptchaerr = "Please confirm that you're not a robot!"
    if lang == 'arabe':
        pwderror = '!التحقق من كلمة المرور'
        mailerr = '!تحقق من بريدك الإلكتروني'
        recaptchaerr = "!الرجاء التأكد من أنك لست آلة"
    if request.method == 'POST':
        req = request.form
        client = Client.find_one({'email': req['email']})
        session['clid'] = client['_id']
        if client:
            a = verify_password(client['password'], req['password'])
            if a:
                if recaptcha.verify():
                    print('recaptcha vérifié! ')
                    session['done'] = True
                    session['client'] = client
                    if len(client['contrats']) == 1:
                        contrat = Contrat.find_one({'_id': client['contrats'][0]})
                        apartement = Propriete.find_one({'_id': contrat['prop_id']})
                        session['apt'] = apartement
                        session['adr_id'] = apartement['adr_id']
                        session['contrat'] = contrat
                    else:
                        session['apt_id'] = 'multiple'
                        session['apt'] = 'multiple'
                        session['contrat'] = 'multiple'
                        session['adr_id'] = 'multiple'
                    return redirect('/preview/' + lang)
                else:
                    error = recaptchaerr
            else:
                error = pwderror
        else:
            error = mailerr
    return render_template("confirm/login.html", lang=lang, error=error)


@app.route("/code_postal", methods=['POST'])  # envoyer la liste des codes postaux
def postal():
    code = request.form['code']
    codes = Adresse.find({'code_postal': code})
    liste = list([])
    for cod in codes:
        liste.append(cod['adresse'] + " :" + str(cod['code_postal']))
    return jsonify({'result': 'success', 'code': code, 'code_list': liste})


@app.route("/vars", methods=['POST'])
def variables():
    apt = Propriete.find_one({'_id': session.get('apt_id')})
    # block d'initialisation des variables
    chambre = int(apt['nbr_chambres'])
    rentown = 0
    if (apt['rentown'] == 'rent'):
        rentown = 10
    else:
        rentown = 20
    alarm = 0
    if apt['sys_alarm'] is True: alarm = 5
    clim = 0
    if apt['climatisation'] is True: clim = 5
    chauf = 0
    if apt['chauffage'] is True: chauf = 5
    type = 10
    if apt['type'] == 'maison':
        type = 15
    elif apt['type']:
        type = 20
    surface = 5
    if apt['surface'] == 'range2':
        surface = 10
    elif apt['surface'] == 'range3':
        surface = 20
    jardin = 0
    if apt['jardin'] is True: jardin = 5
    construction = 0
    if apt['under_construction'] is True: construction = 3
    score = Adresse.find_one({'_id': session.get('adr_id')})['score']
    deductible = int(request.form['deductible'])
    deductible1 = Contrat.find_one({'_id': session.get('cont_id')})['deductible']
    if deductible != deductible1:
        Contrat.update_one({'_id': session.get('cont_id')}, {'$set': {'deductible': deductible}})
    coveragetab = [  # prendre les information de la requete ajax
        int(request.form['properties']),
        int(request.form['liability']),
        int(request.form['medical']),
        int(request.form['house_loss']),
    ]
    if coveragetab[0] > 500: Contrat.update_one(
        {'_id': session.get('cont_id')},
        {'$set': {
            'coverage.0.valeurEstimee': coveragetab[0]
        }}
    )
    if coveragetab[1] > 200: Contrat.update_one(
        {'_id': session.get('cont_id')},
        {'$set': {
            'coverage.1.valeurEstimee': coveragetab[1]
        }}
    )
    if coveragetab[2] > 100: Contrat.update_one(
        {'_id': session.get('cont_id')},
        {'$set': {
            'coverage.2.valeurEstimee': coveragetab[2]
        }}
    )
    if coveragetab[3] > 500: Contrat.update_one(
        {'_id': session.get('cont_id')},
        {'$set': {
            'coverage.3.valeurEstimee': coveragetab[3]
        }}
    )
    coverage = {
        'properties': coveragetab[0],
        'liability': coveragetab[1],
        'medical': coveragetab[2],
        'house_loss': coveragetab[3],
    }
    extratab = [
        int(request.form['jewelry']),
        int(request.form['fineart']),
        int(request.form['bikes']),
        int(request.form['cameras']),
        int(request.form['instruments']),
    ]
    for i in range(5):
        if extratab[i] > 200:
            extra_id = apt['autres_biens'][i]
            AutresBiens.update_one(
                {'_id': extra_id},
                {'$set': {'valeurEstimee': extratab[i]}}
            )
    extra = {
        'jewelry': extratab[0],
        'fineart': extratab[1],
        'bikes': extratab[2],
        'cameras': extratab[3],
        'instruments': extratab[4],
    }
    totcov = 0  # totcov = total de coverage
    for cov in coverage:
        totcov = totcov + coverage[cov] / 20
    totext = 0  # totext = total de extra coverage
    for ext in extra:
        totext = totext + extra[ext] / 20
    #       fin initialisation
    # time.sleep(0)
    formule1 = (((chambre * 5 + rentown + alarm + clim + chauf + type) * surface) + jardin + construction) * int(score)
    formule = formule1 - deductible * 10
    # year_price = random.randint(600000, 1000000)

    # Formule YEAR PRICE = 12x Month Price -12DT
    year_price = formule / 1000 + totext + totcov
    year_sans = formule / 1000
    month_prince = year_price / 12 - year_price * 3 / 100
    year_discount = year_price * 10 / 100
    return jsonify({
        'month_price': month_prince,
        'year_price': year_price,
        'year_discount': year_discount,
        'coverage': coverage,
        'extra': extra
    })


@app.route("/voiture/<nbr>/<lang>")
def voitures(nbr, lang):
    return render_template("voiture/voiture" + nbr + ".html", lang=lang, nbr=nbr)


@app.route('/confirm_email/<token>/<lang>')
def confirm_email(token, lang):
    if lang == 'french':
        token_expired = "Votre confirmation est expirée!"
        token_match_err = "Votre confirmation n'est pas compatible!"
        session_err = "Vous devez ouvrir la page dans la même fenêtre"
        msg = "Votre email est maintenant confirmé, veuillez continuer votre formulaire!"

    elif lang == 'english':
        token_expired = "The confirmation has expired!"
        token_match_err = "The token is not compatible!"
        session_err = "You must open the page in the same window!"
        msg = "Your email is now confirmed, please continue your form!"

    else:
        token_expired = "!إنتهت صلاحية التأكيد"
        token_match_err = "!تأكيدك غير متوافق"
        session_err = "!يجب فتح الصفحة في نفس النافذة"
        msg = "!تم تأكيد البريد الإلكتروني الخاص بك الآن، يرجى متابعة النموذج الخاص بك"

    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
        try:
            if email != session.get('client')['email']:
                return render_template('confirm/confirm.html', confirmed=False, error="not the same email address")
            session.get('client')['confirmed'] = True
        except:
            return render_template('confirm/confirm.html', confirmed=False, error=session_err)
    except SignatureExpired:
        return render_template('confirm/confirm.html', confirmed=False, error=token_expired)
    except BadTimeSignature:
        return render_template('confirm/confirm.html', confirmed=False, error=token_match_err)
    return render_template('confirm/confirm.html', confirmed=True, success=msg, lang=lang)


@app.route('/forgot/pwd/<lang>', methods=['POST'])
def forgot(lang):
    if lang == 'french':
        pwderror = 'Verifiez votre mot de passe !'
        success = 'Votre mot de passe est changé avec succés!'
    if lang == 'english':
        pwderror = 'Verify your password ! '
        success = 'Your password has been changed successfully!'
    if lang == 'arabe':
        pwderror = '!التحقق من كلمة المرور'
        success = '!تم تغيير كلمة المرور بنجاح'
    if request.method == 'POST':
        req = request.form
        if 'gen_code' in req:
            email = req.get('email')
            session['client'] = Client.find_one({'email': email})
            code = random.randrange(10000, 99999)
            session['verificationcode'] = code
            sendCode(email, code)
        if 'code_form' in req:
            code = int(req.get('one') + req.get('two') + req.get('three') + req.get('four') + req.get('five'))
            if code == session.get('verificationcode'):
                return render_template('confirm/resetpwd.html', lang=lang)
        if 'reset_pwd' in req:
            pwd = req.get('password')
            cpwd = req.get('confirm-password')
            if pwd != cpwd:
                return render_template("confirm/resetpwd.html", lang=lang, error=pwderror)
            import re
            pattern = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
            password = pwd
            result = re.findall(pattern, password)
            if not result:
                return render_template("confirm/login.html", lang=lang, error=pwderror)
            session.get('client')['password'] = hash_password(pwd)
            client = session.get('client')
            Client.update_one({'_id': client['_id']}, {'$set': {'password': hash_password(pwd)}})
            print('password changed!')
            return render_template('confirm/login.html', lang=lang, error=success)
    return 'True'


@app.route('/pay/<lang>', methods=['POST'])
def pay(lang):
    if request.method == 'POST':
        req = request.form
        card_num = req.get('card_num')
        date_exp = req.get('date_carte')
        cvc = req.get('cvc')
        try:
            datetime.datetime.strptime(date_exp, '%d/%m/%Y')
        except ValueError:
            return redirect('/preview/'+lang)
        if len(cvc) != 3 or len(card_num) != 16 :
            return redirect('/preview/'+lang)
        client = session.get('client')
        text_association = "this is the contract of the client : "+client['nom']+' '+client['prenom']+" with the id " \
                           +str(session.get('clid'))+" : <br>this contract is paid"
        sendPDF('zied.kanoun6@gmail.com','demande_de_stage.pdf',text_association)
        return 'your payment is successful!'
    return "string"


@app.route('/gen/contract')
def generate():
    client = session.get('client')
    apt = session.get('apt')
    adresse = apt['apt_unit'] +', '+ apt['rue'] +', '+ Adresse.find_one({'_id': session.get('adr_id')})['adresse']
    autre = []
    for one in apt['autres_biens']:
        autre.append(AutresBiens.find_one({'_id': one}))
    rendered = render_template('contrat/contrat.html',
                               client=client,
                               adresse=adresse,
                               valuables=apt['valuables'],
                               autres_biens=autre,
                               contrat=Contrat.find_one({'_id': apt['contrat']}))
    css=['./templates/contrat/contrat.css', './templates/contrat/bootstrap.min.css']
    pdf = pdfkit.from_string(rendered, False,css=css)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = "inline; filename=output.pdf"
    return response


if __name__ == '__main__':
    app.run()
