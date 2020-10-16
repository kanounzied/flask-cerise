import base64
import datetime
import os
import os.path
import random
import uuid

import pdfkit
from bson.objectid import ObjectId
from flask import session, render_template, redirect, request, url_for, abort, jsonify, flash, send_file
from flask_assets import Environment, Bundle
from flask_recaptcha import ReCaptcha
from flask_session import Session
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from werkzeug.utils import secure_filename

# --------------------------add w badel lpath mta3 upload lfile ------------------------------
UPLOAD_FOLDER = os.getcwd() + '/static/public'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
# -------------------------------end-------------------------------------------------------
from classes import *
from db_maker import *
from loadData import load, hash_password, verify_password, loadAuto
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
# ---------------------------------------------add-------------------------------
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# -------------------------------------------------end----------------------------------------


@app.before_request
def make_session_permanent():  # la session est valide pour seulement une heure
    session.permanent = True
    # app.permanent_session_lifetime = timedelta(minutes=60)


# ----------------------------------------------------add----------------------
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def arab():
    return redirect("/home/arabe")


@app.route("/home/<lang>")
def home(lang):
    session.clear()
    return render_template("/home/" + lang + ".html", lang=lang)


@app.route("/clear")
def clear():  # vider la session client
    session.clear()
    return redirect('/')


@app.route('/about/<lang>')
def about(lang):
    return render_template('home/aboutUs.html', lang=lang)


@app.route("/prints")
def prints():  # vider la session client
    print(session)
    return "str(session)"


@app.route("/signup/<nbr>/<lang>", methods=['GET', 'POST'])
def signup(nbr, lang):
    if 'finished' in session:
        return redirect('/preview/' + lang)
    # block des erreurs en trois langues
    if lang == 'french':
        champerr = u'les champs sont vides!'
        adresserr = u"la forme de l'adresse doit etre comme suit : (localité, délégation, gouvernorat)"
        adrnotfound = u"Votre adresse n'est pas enregistrée dans la base de données!"
        chooseerr = u"vous devez choisir!"
        rangeerr = u"vous devez choisir un entier entre 1 et 30 pour les chambres et 50 pour les étages!"
        pwderr = u"votre mot de passe n'est pas le méme!"
        pwdregex = u"mot de passe doit avoir une lettre miniscule, une lettre majuscule, un chiffre, et l'un des " \
                   u"charactéres suivants @#$%^&+= "
        verify = u"Nous vous avons envoyé un mail pour confirmer votre adresse email !"
        emailexisterr = u"Cet email est déja dans la base de données veuillez saisir un autre email!"
        posterr = u"le code postal doit contenir 4 chiffres, si vous avez modifié le code postal, retournez à la page" \
                  u" précédente et choisissez la bonne adresse"
    elif lang == 'english':
        champerr = 'fields are empty!'
        adresserr = "address form must be like : (locality, delegation, governorate)"
        adrnotfound = "Your address is not registered in the database!"
        chooseerr = "you must choose!"
        rangeerr = "you must choose a number in range 1 to 30 rooms or to 50 floors!"
        pwderr = "your password doesn't match!"
        pwdregex = "your password must have a miniscule letter, a capital letter, a number, and one of the following " \
                   "characters @#$%^&+="
        verify = "We've sent you a verification mail for your email address !"
        emailexisterr = "This email is already in data base please type another email!"
        posterr = "postal code must contain 4 numbers, if you have changed the postcode go back to the previous page " \
                  "and choose the right address"
    else:
        champerr = 'الرجاء ملء جميع المعطيات'
        adresserr = "لازم الادريسة هكا : (محافظه، وفد، منطقه)"
        adrnotfound = "عنوانك غير مسجل في قاعدة البيانات!"
        chooseerr = "لازم تختار!"
        pwderr = "كلمة المرور الخاصة بك لا تتطابق!"
        rangeerr = "لازم تختار عدد بين 1 و 30 بيت أو 50 طابق!"
        pwdregex = "يجب أن تحتوي كلمة المرور على الأقل على حرف صغير[a .. z]، حرف كبير[A .. Z]، رقم، واحد من الرموز التالية @#$%^&+="
        verify = "!لقد أرسلنا لك بريد التحقق من عنوان البريد الإلكتروني الخاص بك"
        emailexisterr = "!هذا البريد الإلكتروني موجود في قاعدة البيانات، الرجاء كتابة بريد إلكتروني آخر"
        posterr = "!يجب أن يحتوي الرقم البريدي على 4 أرقام، إذا قمت بتغيير رقم البريد" \
                  " انتقل إلى الصفحة السابقة واختر العنوان الصحيح"
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
            # # # print("client created")
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
            if len(tab) != 3:
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       data=data,
                                       error=adresserr)
            adresseObj = Adresse.find_one(
                {
                    'adresse': adresse
                }
            )
            if adresseObj is None:
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       data=data,
                                       error=adrnotfound)
            # # # print(adresseObj)
            adr_id = adresseObj['_id']
            session['adr_id'] = adr_id
            # # print('address found')
            apt = Propriete_(apt_unit)
            apt.jardin = True
            session['apt'] = apt.__dict__
            # # print('apt created')
            session['form2'] = 'submitted'
        if 'form3' in req:
            adresse = Adresse.find_one({'_id': session['adr_id']})
            adresse1 = adresse['adresse']
            tab = adresse1.split(',')
            city = tab[1]
            state = tab[0]
            apt = session.get('apt')
            # # print(adresse['adresse'])
            under_const = req.get('under_construction')
            post = adresse['code_postal']
            # postal = req.get('code_postal')
            if under_const == "under_construction":
                apt['under_construction'] = True
            else:
                apt['under_construction'] = False
            rue = req.get('adresse')
            if rue == "":
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=champerr,
                                       city=city,
                                       state=state,
                                       code_postal=post,
                                       apt_unit=apt['apt_unit'])
            # if int(postal) not in range(1000,9999):
            #     return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
            #                            error=posterr,
            #                            city=city,
            #                            state=state,
            #                            code_postal=post,
            #                            apt_unit=apt['apt_unit'])
            # if int(post) != int(postal):
            #     return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
            #                            error=posterr,
            #                            city=city,
            #                            state=state,
            #                            code_postal=post,
            #                            apt_unit=apt['apt_unit'])
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
            if (int(room) not in list(range(1, 30))) or (int(etage) not in list(range(100))):
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
                # # print(email, 'none ')
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
        if 'form12b' in req:
            pwderror = ''
            mailerr = ''
            error = ''
            champerr = ''
            recaptchaerr = ''
            if lang == 'french':
                pwderror = 'Verifiez votre mot de passe !'
                mailerr = 'Verifiez votre email !'
                recaptchaerr = "Veuillez confirmer que vous n'êtes pas un robot!"
                champerr = 'les champs sont vides!'
            if lang == 'english':
                pwderror = 'Verify your password ! '
                mailerr = 'Verify your email !'
                recaptchaerr = "Please confirm that you're not a robot!"
                champerr = 'fields are empty!'
            if lang == 'arabe':
                pwderror = '!التحقق من كلمة المرور'
                mailerr = '!تحقق من بريدك الإلكتروني'
                recaptchaerr = "!الرجاء التأكد من أنك لست آلة"
                champerr = 'الرجاء ملء جميع المعطيات'
            if req.get('email') != '':
                client = Client.find_one({'email': req['email']})
                if client:
                    session['clid'] = client['_id']
                    a = verify_password(client['password'], req.get('password'))
                    if a:
                        pwd = req.get('password')
                        if recaptcha.verify():
                            session['client'] = client
                            session['form12'] = 'submitted'
                            session['form13'] = 'submitted'
                            session['form14'] = 'submitted'
                            # print(session.get('client'))
                        else:
                            error = recaptchaerr
                    else:
                        error = pwderror
                else:
                    error = mailerr
            else:
                error = champerr
            if error != '':
                return render_template("signups/signUp12.html", lang=lang, error=error)
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
            adresse = req.get('adresse')
            rue = req.get('rue')
            aptunit = req.get('apt-unit')
            data = list([])
            cursor = Adresse.find({})
            for doc in cursor:  # préparer les adresses de la bd pour la template
                data.append(doc['adresse'])
            if birth == "" or tel == "" or cin == "" or adresse == "" or aptunit == "" or rue == "":
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       data=data,
                                       error=champerr)
            tab = adresse.split(',')
            if len(tab) != 3:
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       data=data,
                                       error=adresserr)
            adresseObj = Adresse.find_one(
                {
                    'adresse': adresse
                }
            )
            if adresseObj is None:
                return render_template("signups/signUp" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       data=data,
                                       error=adrnotfound)
            session.get('client')['date_de_naissance'] = birth
            session.get('client')['tel_num'] = tel
            session.get('client')['cin'] = cin
            session.get('client')['adresse'] = aptunit + ' ' + rue + ', ' + adresse
            session.get('client')['code-postal'] = Adresse.find_one({'adresse': adresse})['code_postal']
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
        # # # print("client already conneted")
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
            apt = Propriete.find_one({'_id': session['apt_id']})
            autre = []
            # print(apt)
            for one in apt['autres_biens']:
                autre.append(AutresBiens.find_one({'_id': one}))
            rendered = render_template('contrat/contrat.html',
                                       client=client,
                                       adresse=adresse,
                                       valuables=apt['valuables'],
                                       autres_biens=autre,
                                       contrat=Contrat.find_one({'_id': apt['contrat']}))
            css = ['./templates/contrat/contrat.css', './templates/contrat/bootstrap.min.css']
            pdf = pdfkit.from_string(rendered, False, css=css)
            text_societe = "this is the contract of the client : " + client['nom'] + ' ' + client[
                'prenom'] + " with the id " \
                           + str(session.get('clid')) + " : <br>this contract is still not paid"
            sendPDF('zied.kanoun6@gmail.com', pdf, text_societe, 'immobiliere')
            sendPDF('henimaher@gmail.com', pdf, text_societe, 'immobiliere')
            text_client = "the contract is ready now and waiting to be paid!<br> if you want to modify it just log in and choose" \
                          " your contract if you have more than one"
            sendPDF(client['email'], pdf, text_client, 'immobiliere')
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
        session['apt'] = Propriete.find_one({'_id': session.get('apt_id')})
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
        voitures = list([])
        if 'contrats' in client:
            for cont in client['contrats']:
                try:
                    cnt = Contrat.find_one({'_id': cont})
                    if 'paid' in cnt:
                        paid = True
                    else:
                        paid = False
                    apt = Propriete.find_one({'_id': cnt['prop_id']})
                    adresse = Adresse.find_one({'_id': apt['adr_id']})['adresse']
                    print('cnt', cont)
                    prop = {
                        'adresse': apt['apt_unit'] + ", " + apt['rue'] + "  " + adresse,
                        'paid': paid
                    }
                    proprietes.append(prop)
                except:
                    print(cont, ' not found in Contrat')
        if 'contratsV' in client:
            for cont in client['contratsV']:
                try:
                    cnt = Contrat_voiture.find_one({'_id': cont})
                    if 'paid' in cnt:
                        paid = True
                    else:
                        paid = False
                    garid = cnt['garantie_id']
                    carid = Garantie.find_one({'_id': garid})['voiture_id']
                    car = Voiture.find_one({'_id': carid})
                    voit = {
                        'car': car['marq_model'] + ', ' + car['matricule'],
                        'paid': paid
                    }
                    voitures.append(voit)
                except:
                    print('car not found')
        return render_template("resultat/multiple.html", contrats=proprietes, voitures=voitures, lang=lang)


@app.route("/login/<lang>", methods=['POST', 'GET'])
def login(lang):
    pwderror = ''
    mailerr = ''
    error = ''
    champerr = ''
    if lang == 'french':
        pwderror = 'Verifiez votre mot de passe !'
        mailerr = 'Verifiez votre email !'
        recaptchaerr = "Veuillez confirmer que vous n'êtes pas un robot!"
        champerr = 'les champs sont vides!'
    if lang == 'english':
        pwderror = 'Verify your password ! '
        mailerr = 'Verify your email !'
        recaptchaerr = "Please confirm that you're not a robot!"
        champerr = 'fields are empty!'
    if lang == 'arabe':
        pwderror = '!التحقق من كلمة المرور'
        mailerr = '!تحقق من بريدك الإلكتروني'
        recaptchaerr = "!الرجاء التأكد من أنك لست آلة"
        champerr = 'الرجاء ملء جميع المعطيات'
    if request.method == 'POST':
        req = request.form
        if req.get('email') != '':
            client = Client.find_one({'email': req['email']})
            if client:
                session['clid'] = client['_id']
                a = verify_password(client['password'], req['password'])
                if a:
                    if recaptcha.verify():
                        session['done'] = True
                        session['client'] = client
                        if 'carreport' in req:
                            return redirect('/addreport/8/' + lang)
                        nbr_conts = 0
                        if 'contrats' in client and len(client['contrats']) > 0: nbr_conts += len(client['contrats'])
                        if 'contratsV' in client and len(client['contratsV']) > 0: nbr_conts += len(client['contratsV'])
                        if 'contrats_vie' in client and len(client['contrats_vie'])>0: nbr_conts += len(client['contrats_vie'])
                        if nbr_conts == 1:
                            if 'contrats' in client and len(client['contrats']) == 1 and 'paid' not in Contrat.find_one(
                                    {'_id': client['contrats'][0]}):
                                contrat = Contrat.find_one({'_id': client['contrats'][0]})
                                apartement = Propriete.find_one({'_id': contrat['prop_id']})
                                session['apt'] = apartement
                                session['adr_id'] = apartement['adr_id']
                                session['contrat'] = contrat
                                session['finished'] = True
                                return redirect('/preview/' + lang)
                            if 'contratsV' in client and len(
                                    client['contratsV']) == 1 and 'paid' not in Contrat_voiture.find_one(
                                    {'_id': client['contratsV'][0]}):
                                contrat = Contrat_voiture.find_one({'_id': client['contratsV'][0]})
                                apartement = Propriete.find_one({'_id': contrat['prop_id']})
                                session['apt'] = apartement
                                session['adr_id'] = apartement['adr_id']
                                session['contrat'] = contrat
                                session['finished'] = True
                                return redirect('/previewvoiture/' + lang)
                            error = 'all of your contracts are paid'
                        else:
                            session['apt_id'] = 'multiple'
                            session['apt'] = 'multiple'
                            session['contrat'] = 'multiple'
                            session['adr_id'] = 'multiple'
                        session['finished'] = True
                        return redirect('/preview/' + lang)
                    else:
                        error = recaptchaerr
                else:
                    error = pwderror
            else:
                error = mailerr
        else:
            error = champerr
    elif 'clid' in session:
        client = session['client']
        if len(client['contrats']) == 1 and 'paid' not in Contrat.find_one({'_id': client['contrats'][0]}):
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
        session['finished'] = True
        return redirect('/preview/' + lang)
    return render_template("confirm/login.html", lang=lang, error=error)


@app.route("/code_postal", methods=['POST'])  # envoyer la liste des codes postaux
def postal():
    code = int(request.form['code'])
    # print('code', code)
    codes = Adresse.find({'code_postal': code})
    liste = list([])
    for cod in codes:
        liste.append(cod['adresse'] + " :" + str(cod['code_postal']))
    # print(liste)
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
    deductible1 = Contrat.find_one({'_id': apt['contrat']})['deductible']
    if deductible != deductible1:
        Contrat.update_one({'_id': apt['contrat']}, {'$set': {'deductible': deductible}})
    coveragetab = [  # prendre les information de la requete ajax
        int(request.form['properties']),
        int(request.form['liability']),
        int(request.form['medical']),
        int(request.form['house_loss']),
    ]
    if coveragetab[0] > 500: Contrat.update_one(
        {'_id': apt['contrat']},
        {'$set': {
            'coverage.0.valeurEstimee': coveragetab[0]
        }}
    )
    if coveragetab[1] > 200: Contrat.update_one(
        {'_id': apt['contrat']},
        {'$set': {
            'coverage.1.valeurEstimee': coveragetab[1]
        }}
    )
    if coveragetab[2] > 100: Contrat.update_one(
        {'_id': apt['contrat']},
        {'$set': {
            'coverage.2.valeurEstimee': coveragetab[2]
        }}
    )
    if coveragetab[3] > 500: Contrat.update_one(
        {'_id': apt['contrat']},
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
    month_prince = year_price / 12
    year_discount = year_price * 10 / 100
    session['price_house'] = {
        'month_prince': month_prince,
        'year_price': year_price - year_discount
    }
    return jsonify({
        'month_price': month_prince,
        'year_price': year_price,
        'year_discount': year_discount,
        'coverage': coverage,
        'extra': extra
    })


@app.route('/confirm_email/<token>/<lang>', methods=['POST', 'GET'])
def confirm_email(token, lang):
    target = 'confirm/confirm.html'
    if lang in ['ar', 'fr', 'en']:
        target = 'confirm/confirmvie.html'
    if lang == 'french':
        token_expired = u"Votre confirmation est expirée!"
        token_match_err = "Votre confirmation n'est pas compatible!"
        session_err = "Vous devez ouvrir la page dans la même fenêtre"
        msg = u"Votre email est maintenant confirmé, veuillez continuer votre formulaire!"

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
            return render_template(target, confirmed=False, error=session_err)
    except SignatureExpired:
        return render_template(target, confirmed=False, error=token_expired)
    except BadTimeSignature:
        return render_template(target, confirmed=False, error=token_match_err)
    return render_template(target, confirmed=True, success=msg, lang=lang)


@app.route('/forgot/pwd/<lang>', methods=['POST'])
def forgot(lang):
    if lang == 'french':
        emailerr = "cet email n'existe pas dans la bd !"
        pwderror = 'Verifiez votre mot de passe !'
        success = u'Votre mot de passe est changé avec succés!'
        codeerr = "Le code n'est pas valide"
    if lang == 'english':
        emailerr = "this email doesn't exist!"
        pwderror = 'Verify your password ! '
        success = 'Your password has been changed successfully!'
        codeerr = "the code is not valid"
    if lang == 'arabe':
        emailerr = "cet email n'existe pas dans la bd !"
        pwderror = '!التحقق من كلمة المرور'
        success = '!تم تغيير كلمة المرور بنجاح'
        codeerr = "الرمز غير صالح"
    if request.method == 'POST':
        req = request.form
        if 'gen_code' in req:
            email = req.get('email')
            client = Client.find_one({'email': email})
            if client:
                session['client'] = client
                code = random.randrange(10000, 99999)
                session['verificationcode'] = code
                sendCode(email, code)
            else:
                # print('lahna')
                return jsonify({'error': emailerr})
        if 'code_form' in req:
            try:
                code = int(req.get('one') + req.get('two') + req.get('three') + req.get('four') + req.get('five'))
            except:
                return render_template('confirm/login.html', lang=lang, error=codeerr)
            if code == session.get('verificationcode'):
                return render_template('confirm/resetpwd.html', lang=lang)
            else:
                return render_template('confirm/login.html', lang=lang, error=codeerr)
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
            session['client']['password'] = hash_password(pwd)
            client = session.get('client')
            Client.update_one({'_id': client['_id']}, {'$set': {'password': hash_password(pwd)}})
            # # print('password changed!')
            return render_template('confirm/login.html', lang=lang, error=success)
    return 'False'


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
            return redirect('/preview/' + lang)
        if len(cvc) != 3 or len(card_num) != 16:
            return redirect('/preview/' + lang)
        client = session.get('client')
        text_societe = "this is the contract of the client : " + client['nom'] + ' ' + client[
            'prenom'] + " with the id " \
                       + str(session.get('clid')) + " : <br>this contract is paid"
        text_client = "you have just paid your contract for" + str(session.get('price_house')['year_price']) + "dt"
        apt = session.get('apt')
        adresse = apt['apt_unit'] + ', ' + apt['rue'] + ', ' + Adresse.find_one({'_id': session.get('adr_id')})[
            'adresse']
        autre = []
        # print(apt)
        for one in apt['autres_biens']:
            autre.append(AutresBiens.find_one({'_id': one}))
        rendered = render_template('contrat/contrat.html',
                                   client=client,
                                   adresse=adresse,
                                   valuables=apt['valuables'],
                                   autres_biens=autre,
                                   contrat=Contrat.find_one({'_id': apt['contrat']}))
        css = ['./templates/contrat/contrat.css', './templates/contrat/bootstrap.min.css']
        pdf = pdfkit.from_string(rendered, False, css=css)
        sendPDF(client['email'], pdf, text_client, 'immobiliere')
        sendPDF('zied.kanoun6@gmail.com', pdf, text_societe, 'immobiliere')
        sendPDF('henimaher@gmail.com', pdf, text_societe, 'immobiliere')
        Contrat.update_one({'prop_id': apt['_id']}, {"$set": {'paid': True}})
        session['done'] = True
        session['client'] = client
        session['apt_id'] = 'multiple'
        session['apt'] = 'multiple'
        session['contrat'] = 'multiple'
        session['adr_id'] = 'multiple'
        session['finished'] = True
    return redirect("/preview/" + lang)


@app.route('/gen/contract')
def generate():
    client = session.get('client')
    apt = session.get('apt')
    adresse = apt['apt_unit'] + ', ' + apt['rue'] + ', ' + Adresse.find_one({'_id': session.get('adr_id')})['adresse']
    autre = []
    # preparer la liste des autres biens
    for one in apt['autres_biens']:
        autre.append(AutresBiens.find_one({'_id': one}))
    rendered = render_template('contrat/contrat.html',
                               client=client,
                               adresse=adresse,
                               valuables=apt['valuables'],
                               autres_biens=autre,
                               contrat=Contrat.find_one({'_id': apt['contrat']}))
    css = ['./templates/contrat/contrat.css', './templates/contrat/bootstrap.min.css']
    pdf = pdfkit.from_string(rendered, False, css=css)
    sendPDF('zied.kanoun6@gmail.com', pdf, 'test pdf 12 12 12', 'test')
    sendPDF('henimaher@gmail.com', pdf, 'test pdf 12 12 12', 'test')
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = "inline; filename=output.pdf"
    return response


@app.route('/delete/<ins>/<pos>', methods=['POST'])
def delete(ins, pos):
    client = session.get('client')
    if ins == "houseins":
        cont_id = client['contrats'][int(pos) - 1]
        # print(cont_id)
        prop = Propriete.find_one({'contrat': cont_id})
        prop_id = prop['_id']
        adr_id = prop['adr_id']
        autres = list(prop['autres_biens'])
        Propriete.delete_one({'contrat': cont_id})
        Contrat.delete_one({'_id': cont_id})
        liste = list(Client.find_one({'_id': client['_id']})['contrats'])
        liste.remove(cont_id)
        Client.update_one({'_id': client['_id']}, {'$set': {'contrats': liste}})
        liste = list(Adresse.find_one({'_id': adr_id})['proprietes'])
        liste.remove(prop_id)
        Adresse.update_one({'_id': adr_id}, {'$set': {'proprietes': liste}})
        for autre in autres:
            # print(autre)
            AutresBiens.delete_one({'_id': autre})
        session['client'] = Client.find_one({'_id': client['_id']})
    elif ins == 'carins':
        cont_id = client['contratsV'][int(pos) - 1]
        liste = list(Client.find_one({'_id': client['_id']})['contratsV'])
        liste.remove(cont_id)
        Client.update_one({'_id': client['_id']}, {'$set': {'contratsV': liste}})
        garid = Contrat_voiture.find_one({'_id': cont_id})['garantie_id']
        Contrat_voiture.delete_one({'_id': cont_id})
        voitid = Garantie.find_one({'_id': garid})['voiture_id']
        Garantie.delete_one({'_id': garid})
        Voiture.delete_one({'_id': voitid})
        session['client'] = Client.find_one({'_id': client['_id']})
    elif ins == 'lifeins':
        print('mazel')
    return 'nothing'


########### 5edmet beya ##############
@app.route("/voiture/<nbr>/<lang>", methods=['GET', 'POST'])
def voiture(nbr, lang):
    if lang == 'french':
        chooseerr = u"vous devez choisir!"
        champerr = u'les champs sont vides!'
        champwrg2 = u'S.V.P verifiez vos informations! La valeur actuelle ne peut pas être superieure à la valeur à neuf!'
        champwrg3 = u'Les valeurs ne peuvent pas être moins de 1000DT!'
        champwrg4 = u'Veuillez saisir que des lettres!'
        champwrg5 = u'Veuillez écrire votre numéro d\'immatriculation de la même manière que l\'exemple! N\'oubliez pas les espaces.'
        champwrg6 = u'Vous avez peut-être fait une erreur de frappe! Veuillez écrire correctement votre numéro d\'immatriculation!'
        emailexisterr = u"Cet email est déja dans la base de données veuillez saisir un autre email!"
        pwderr = u"votre mot de passe n'est pas le méme!"
        pwdregex = u"mot de passe doit avoir une lettre miniscule, une lettre majuscule, un chiffre, et l'un des " \
                   u"charactéres suivants @#$%^&+= "
        verify = u"Nous vous avons envoyé un mail pour confirmer votre adresse email !"
    elif lang == "english":
        champerr = 'Fields are empty!'
        chooseerr = "You have to choose!"
        champwrg2 = 'Please verify your information! The current value cannot be higher than the new vehicle value!'
        champwrg3 = 'The values cannot be less than 1000DT!'
        champwrg4 = 'Please enter only numbers!'
        champwrg5 = 'Please write your registration number as the same way as the example! Don\'t forget the spaces.'
        champwrg6 = 'You may be made a typing error! Please write your registration number correctly!'
        emailexisterr = "This email is already in data base please type another email!"
        pwdregex = "your password must have a miniscule letter, a capital letter, a number, and one of the following " \
                   "characters @#$%^&+="
        pwderr = "your password doesn't match!"
        verify = "We've sent you a verification mail for your email address !"
    else:
        champerr = 'الرجاء ملء جميع المعطيات'
        chooseerr = "لازم تختار"
        champwrg2 = '!زيد ثبت! قيمة الكرهبة الحالية ما تنجمش تكون أكبر من قيمة الكرهبة وهي جديدة'
        champwrg3 = '!القيمتين ما ينجموش يكونوا أقل من 1000 دينار'
        champwrg4 = '!الرجاء إدخال أرقام فقط'
        champwrg5 = '.يرجى كتابة رقم التسجيل الخاص بك بنفس طريقة المثال! لا تنس المساحات'
        champwrg6 = '!ربما تكون قد ارتكبت خطأ في الكتابة! الرجاء كتابة رقم التسجيل الخاص بك بشكل صحيح'
        emailexisterr = "!هذا البريد الإلكتروني موجود في قاعدة البيانات، الرجاء كتابة بريد إلكتروني آخر"
        pwderr = "كلمة المرور الخاصة بك لا تتطابق!"
        pwdregex = "يجب أن تحتوي كلمة المرور على الأقل على حرف صغير[a .. z]، حرف كبير[A .. Z]، رقم، واحد من الرموز التالية @#$%^&+="
        verify = "!لقد أرسلنا لك بريد التحقق من عنوان البريد الإلكتروني الخاص بك"
    if request.method == "POST":
        req = request.form
        if 'vform1' in req:
            prenom = req.get('first_name')
            nom = req.get('last_name')
            if nom == "" or prenom == "":
                return render_template("/voiture/register/voiture" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1,
                                       lang=lang,
                                       error=champerr)

            client = Client_(prenom, nom)
            session['client'] = client.__dict__
            print('client created')
            session['vform1'] = 'submitted'
        if 'vform1' not in session:
            return redirect('/voiture/1/' + lang)

        if 'vform2' in req:
            typev = req.get('typev')
            if typev is None:
                return render_template("voiture/register/voiture" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1,
                                       lang=lang,
                                       error=chooseerr)
            if typev not in ['passenger', 'taxi', 'commercial', None]:
                return render_template("voiture/register/voiture" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1,
                                       lang=lang,
                                       error="please do not change values!")
            session['typev'] = typev
            voiture = Voiture_(typev)
            session['voiture'] = voiture.__dict__
            session['vform2'] = 'submitted'
        if 'vform3' in req:
            valeur_a_neuf = req.get('valeur_a_neuf')
            valeur_actuelle = req.get('valeur_actuelle')
            if valeur_a_neuf == "" or valeur_actuelle == "":
                return render_template("/voiture/register/voiture" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1,
                                       lang=lang,
                                       error=champerr)
            if int(valeur_actuelle) > int(valeur_a_neuf):
                return render_template("/voiture/register/voiture" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1,
                                       lang=lang,
                                       error=champwrg2)
            if len(valeur_a_neuf) < 4 or len(valeur_actuelle) < 4:
                return render_template("/voiture/register/voiture" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1,
                                       lang=lang,
                                       error=champwrg3)
            for i in range(len(valeur_a_neuf)):
                if valeur_a_neuf[i].isalpha():
                    return render_template("/voiture/register/voiture" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1,
                                           lang=lang,
                                           error=champwrg4)
            for j in range(len(valeur_actuelle)):
                if valeur_actuelle[j].isalpha():
                    return render_template("/voiture/register/voiture" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1,
                                           lang=lang,
                                           error=champwrg4)

            session.get('voiture')['valeur_a_neuf'] = valeur_a_neuf
            session.get('voiture')['valeur_actuelle'] = valeur_actuelle
            session['vform3'] = 'submitted'
        if 'vform4' in req:
            matricule = req.get('matricule')
            marque = req.get('marque')
            modele = req.get('modele')
            if matricule == "":
                return render_template("/voiture/register/voiture" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1,
                                       lang=lang,
                                       error=champerr)
            if lang == 'arabe':
                word = matricule.split(" ")
                if word[0] == matricule:
                    return render_template("/voiture/register/voiture" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1,
                                           lang=lang,
                                           error=champwrg5)
                if len(word[0]) > 3:
                    return render_template("/voiture/register/voiture" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1,
                                           lang=lang,
                                           error=champwrg6)
                if len(word[0]) < 2:
                    return render_template("/voiture/register/voiture" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1,
                                           lang=lang,
                                           error=champwrg6)
                for j in range(len(word[0])):
                    if word[0][j].isalpha():
                        return render_template("/voiture/register/voiture" + str(int(nbr) - 1) + ".html",
                                               nbr=int(nbr) - 1, lang=lang,
                                               error=champwrg5)
                if word[1] not in ['تونس', 'tun', 'TUN']:
                    return render_template("/voiture/register/voiture" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1,
                                           lang=lang,
                                           error=champwrg5)
                if len(word[2]) > 4:
                    return render_template("/voiture/register/voiture" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1,
                                           lang=lang,
                                           error=champwrg6)
                if len(word[2]) < 1:
                    return render_template("/voiture/register/voiture" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1,
                                           lang=lang,
                                           error=champwrg6)
                for m in range(len(word[2])):
                    if word[2][m].isalpha():
                        return render_template("/voiture/register/voiture" + str(int(nbr) - 1) + ".html",
                                               nbr=int(nbr) - 1, lang=lang,
                                               error=champwrg5)
            else:
                word = matricule.split(" ")
                if word[0] == matricule:
                    return render_template("/voiture/register/voiture" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1,
                                           lang=lang,
                                           error=champwrg5)
                if len(word[0]) > 3:
                    return render_template("/voiture/register/voiture" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1,
                                           lang=lang,
                                           error=champwrg6)
                if len(word[0]) < 2:
                    return render_template("/voiture/register/voiture" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1,
                                           lang=lang,
                                           error=champwrg6)
                for j in range(len(word[0])):
                    if word[0][j].isalpha():
                        print('aaa')
                        return render_template("/voiture/register/voiture" + str(int(nbr) - 1) + ".html",
                                               nbr=int(nbr) - 1, lang=lang,
                                               error=champwrg5)
                if word[1] != 'TUN':
                    print('bbb')
                    return render_template("/voiture/register/voiture" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1,
                                           lang=lang,
                                           error=champwrg5)
                if len(word[2]) > 4:
                    return render_template("/voiture/register/voiture" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1,
                                           lang=lang,
                                           error=champwrg6)
                if len(word[2]) < 1:
                    return render_template("/voiture/register/voiture" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1,
                                           lang=lang,
                                           error=champwrg6)
                for m in range(len(word[2])):
                    if word[2][m].isalpha():
                        return render_template("/voiture/register/voiture" + str(int(nbr) - 1) + ".html",
                                               nbr=int(nbr) - 1, lang=lang,
                                               error=champwrg5)
            if marque == "Select brand" or marque == "Sélectionner la marque" or marque == "إختار الماركة":
                return render_template("voiture/register/voiture" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1,
                                       lang=lang,
                                       error=chooseerr)
            if modele == "Select model" or modele == "Sélectionner le modèle" or modele == "إختار موديل":
                return render_template("voiture/register/voiture" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1,
                                       lang=lang,
                                       error=chooseerr)
            session.get('voiture')['marq_model'] = marque + " " + modele
            session.get('voiture')['matricule'] = matricule
            session['vform4'] = 'submitted'
        if 'vform5' in req:
            classe = req.get('classe')

            if classe == "Select a class" or classe == "Sélectionner la classe" or classe == "إختار القسم":
                return render_template("voiture/register/voiture" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1,
                                       lang=lang,
                                       error=chooseerr)
            nbcv = req.get('nbcv')

            if nbcv == "Select" or nbcv == "Sélectionner" or nbcv == "إختار":
                return render_template("voiture/register/voiture" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1,
                                       lang=lang,
                                       error=chooseerr)
            session.get('voiture')['bonus_malus'] = classe
            session.get('voiture')['puissance'] = nbcv
            session['vform5'] = 'submitted'
        if 'vform6' in req:
            remorquage = req.get('remorquage')
            if remorquage == "remorquage_non":
                remorquage = "EXCLUE"
            else:
                remorquage = "OUI"
            pers_trans = req.get('pers_trans')
            nbp = req.get('nbp')
            capital_d1 = req.get('capital_d')
            size = len(capital_d1)
            capital_d = capital_d1[:size - 2]
            if pers_trans == 'pers_trans_oui':
                if nbp == "Select" or nbp == "Sélectionner" or nbp == "إختار":
                    return render_template("voiture/register/voiture" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1,
                                           lang=lang,
                                           error=chooseerr)
            if pers_trans == "pers_trans_non":
                pers_trans = "EXCLUE"
                nbp = "EXCLUE"
                capital_d = "EXCLUE"

            session['pers_trans'] = pers_trans
            garantie = GarantieAuto_(remorquage, nbp, capital_d)
            session['garantie'] = garantie.__dict__
            session['vform6'] = 'submitted'
        if 'vform7' in req:
            bris_glace = req.get('bris_glace')
            radio_ca7 = req.get('radio_ca7')
            valeur_bg = req.get('valeur_bg')
            valeur_rc = req.get('valeur_rc')
            if bris_glace == "bris_glace_non":
                valeur_bg = "EXCLUE"
            else:
                if valeur_bg == "":
                    return render_template("/voiture/register/voiture" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1,
                                           lang=lang,
                                           error=champerr)
                for i in range(len(valeur_bg)):
                    if valeur_bg[i].isalpha():
                        return render_template("/voiture/register/voiture" + str(int(nbr) - 1) + ".html",
                                               nbr=int(nbr) - 1, lang=lang,
                                               error=champwrg4)
            if radio_ca7 == 'radio_ca7_non':
                valeur_rc = "EXCLUE"
            else:
                if valeur_rc == "":
                    return render_template("/voiture/register/voiture" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1,
                                           lang=lang,
                                           error=champerr)
                for j in range(len(valeur_rc)):
                    if valeur_rc[j].isalpha():
                        return render_template("/voiture/register/voiture" + str(int(nbr) - 1) + ".html",
                                               nbr=int(nbr) - 1, lang=lang,
                                               error=champwrg4)
            session['bris_glace'] = bris_glace
            session.get('garantie')['valeur_bg'] = valeur_bg
            session['radio_ca7'] = radio_ca7
            session.get('garantie')['valeur_rc'] = valeur_rc
            session['vform7'] = 'submitted'
        if 'vform8' in req:
            conducteur_plus = req.get('conducteur_plus')
            capital_assure_cp1 = req.get('capital_assure_cp')
            size1 = len(capital_assure_cp1)
            capital_assure_cp = capital_assure_cp1[:size1 - 2]
            if conducteur_plus == "conducteur_plus_non":
                conducteur_plus = "EXCLUE"
                capital_assure_cp = "EXCLUE"
            else:
                conducteur_plus = "OUI"
            damage = req.get('damage')
            incendie = session.get('voiture')['valeur_actuelle']
            capital_assure_d1 = req.get('capital_assure_d')
            size2 = len(capital_assure_d1)
            capital_assure_d = capital_assure_d1[:size2 - 2]
            franchise = req.get('franchise')
            if damage == "damage_basique":
                dommage_collision = "EXCLUE"
                dommage_tous_risques = "EXCLUE"
                capital_assure_d = "EXCLUE"
                franchise = "EXCLUE"
            elif damage == "damage_col":
                dommage_tous_risques = "EXCLUE"
                dommage_collision = capital_assure_d
                franchise = ""
            else:
                dommage_collision = "EXCLUE"
                dommage_tous_risques = incendie
            session.get('garantie')['conducteur_plus'] = conducteur_plus
            session.get('garantie')['capital_assure_cp'] = capital_assure_cp
            session['damage'] = damage
            session.get('garantie')['incendie'] = incendie
            session['capital_assure_d'] = capital_assure_d
            session.get('garantie')['franchise'] = franchise
            session.get('garantie')['dommage_collision'] = dommage_collision
            session.get('garantie')['dommage_tous_risques'] = dommage_tous_risques
            session['vform8'] = 'submitted'
        if 'vform9' in req:
            email = req.get('email')
            if email == "":
                # # print(email, 'none ')
                return render_template("voiture/register/voiture" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1,
                                       lang=lang,
                                       error=champerr)
            session.get('client')['email'] = email
            client = session.get('client')
            if Client.find_one({'email': client['email']}):  # client already in data base
                return render_template("voiture/register/voiture" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1,
                                       lang=lang,
                                       error=emailexisterr)
            token = s.dumps(email, salt='email-confirm')
            link = url_for('confirm_email_v', lang=lang, token=token, _external=True)
            sendConfirm(email, link)
            # session['email'] = email
            session['vform9'] = 'submitted'
            return render_template('confirm/confirmv.html', confirmed=False, error=verify, lang=lang)

        if 'vform9b' in req:
            pwderror = ''
            mailerr = ''
            error = ''
            champerr = ''
            recaptchaerr = ''
            if lang == 'french':
                pwderror = 'Verifiez votre mot de passe !'
                mailerr = 'Verifiez votre email !'
                recaptchaerr = "Veuillez confirmer que vous n'êtes pas un robot!"
                champerr = 'les champs sont vides!'
            if lang == 'english':
                pwderror = 'Verify your password ! '
                mailerr = 'Verify your email !'
                recaptchaerr = "Please confirm that you're not a robot!"
                champerr = 'fields are empty!'
            if lang == 'arabe':
                pwderror = '!التحقق من كلمة المرور'
                mailerr = '!تحقق من بريدك الإلكتروني'
                recaptchaerr = "!الرجاء التأكد من أنك لست آلة"
                champerr = 'الرجاء ملء جميع المعطيات'
            if req.get('email') != '':
                client = Client.find_one({'email': req['email']})
                if client:
                    session['clid'] = client['_id']
                    a = verify_password(client['password'], req.get('password'))
                    if a:
                        pwd = req.get('password')
                        if recaptcha.verify():
                            session['client'] = client
                            session['vform9'] = 'submitted'
                            session['vform10'] = 'submitted'
                            session['vform11'] = 'submitted'
                            # print(session.get('client'))
                        else:
                            error = recaptchaerr
                    else:
                        error = pwderror
                else:
                    error = mailerr
            else:
                error = champerr
            if error != '':
                return render_template("voiture/register/voiture9.html", lang=lang, error=error)
        if 'vform10' in req:
            pwd = req.get('password')
            cpwd = req.get('confirm-password')
            if pwd != cpwd:
                return render_template("voiture/register/voiture" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1,
                                       lang=lang,
                                       error=pwderr)
            import re
            pattern = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
            password = pwd
            result = re.findall(pattern, password)
            if not result:
                return render_template("voiture/register/voiture" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1,
                                       lang=lang,
                                       error=pwdregex)
            session.get('client')['password'] = hash_password(pwd)
            # session['password'] = pwd
            # session['confirm-password'] = cpwd
            session['vform10'] = 'submitted'
        if 'vform11' in req:
            tel = req.get('tel')
            cin = req.get('cin')
            birth = req.get('birth')
            adresse = req.get('adresse')
            rue = req.get('rue')
            aptunit = req.get('apt-unit')
            data = list([])
            cursor = Adresse.find({})
            for doc in cursor:  # préparer les adresses de la bd pour la template
                data.append(doc['adresse'])
            if birth == "" or tel == "" or cin == "" or adresse == '' or rue == "" or aptunit == "":
                return render_template("voiture/register/voiture" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1,
                                       lang=lang,
                                       data=data,
                                       error=champerr)
            tab = adresse.split(',')
            if len(tab) != 3:
                return render_template("voiture/register/voiture" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1,
                                       lang=lang,
                                       data=data,
                                       error='address not in data base!')
            adresseObj = Adresse.find_one(
                {
                    'adresse': adresse
                }
            )
            if adresseObj is None:
                return render_template("voiture/register/voiture" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1,
                                       lang=lang,
                                       data=data,
                                       error='address not in data base!')
            session.get('client')['date_de_naissance'] = birth
            session.get('client')['tel_num'] = tel
            session.get('client')['cin'] = cin
            session.get('client')['adresse'] = aptunit + ' ' + rue + ', ' + adresse
            session.get('client')['code-postal'] = Adresse.find_one({'adresse': adresse})['code_postal']
            session['vform11'] = 'submitted'

    if session == {'_permanent': True} and int(nbr) > 1:  # if session vide wenti moch fel page 1
        return redirect("/voiture/1/" + lang)
    if int(nbr) in range(2, 12) and ('vform' + str(int(nbr) - 1) not in session):
        form = ""
        for i in range(2, 12):
            print(i)
            if ('vform' + str(i)) in session:
                form = str(i)
            print(form)
        return redirect("/voiture/" + form + "/" + lang)

    if nbr == "12" and request.method == 'POST':

        if session.get('client')['confirmed']:
            voiture = session.get('voiture')
            client = session.get('client')
            garantie = session.get('garantie')
            loadAuto(client, voiture, garantie)
            contratv = Contrat_voiture.find_one({'_id': session.get('contv_id')})
            print(contratv)
            session['loaded'] = True
            session['done'] = True
            session['finished'] = True  # finished is for when the client submits the last form (passwords) and from
            # then he shouldn't be allowed to return to signups
            garantie = Garantie.find_one({'_id': session.get('garid')})
            rendered = render_template('contrat_voiture/contrat_voiture.html',
                                       client=client,
                                       garantie=garantie,
                                       contratv=contratv)
            css = ['./templates/contrat/contrat.css', './templates/contrat/bootstrap.min.css']
            pdf = pdfkit.from_string(rendered, False, css=css)
            text_societe = "This is the contract of the client : " + client['prenom'] + ' ' + client[
                'nom'] + " with the id " \
                           + str(session.get('client_id')) + " : <br>this contract is still not paid"
            sendPDF('henimaher@gmail.com', pdf, text_societe, 'voiture')
            text_client = "The contract is ready now and waiting to be paid!<br> If you want to modify it just log in and choose" \
                          " your contract if you have more than one"
            sendPDF(client['email'], pdf, text_client, 'voiture')
            # return redirect(url_for('gen/contract/voiture')
            return redirect("/previewvoiture/" + lang)
    elif nbr == "12" and request.method == 'GET':
        print('df')
        abort(403)

    if int(nbr) > 9 and session.get('client')['confirmed'] == False:
        return render_template('confirm/confirm.html', confirmed=False, error=verify, lang=lang)

    return render_template("voiture/register/voiture" + nbr + ".html", nbr=nbr, lang=lang)


@app.route("/previewvoiture/<lang>", defaults={'index': '0'})
@app.route("/previewvoiture/<lang>/<index>")
def previewV(lang, index):
    if index != '0':
        client = session.get('client')
        contratvid = client['contratsV'][int(index) - 1]
        contratv = Contrat_voiture.find_one({'_id': contratvid})
        client_id = client['_id']
        void = Voiture.find_one({'client_id': client_id})['_id']
        garantie = Garantie.find_one({'_id': contratv['garantie_id']})
        session['garid'] = garantie['_id']
        session['garantie'] = garantie
        session['contratv'] = contratv
        session['void'] = void
    client = session.get('client')
    email = client['email']
    client_id = Client.find_one({'email': email})['_id']
    void = session.get('void')
    if void != 'multiple':
        voit = Voiture.find_one({'_id': void})
        voiture = voit['marq_model'] + " " + voit['matricule']
        garantie = session.get('garantie')
        done = False  # pour afficher la page de preload
        if 'done' in session:
            done = True
        return render_template("resultat/previewvoiture.html",
                               lang=lang,
                               done=done,
                               voiture=voiture
                               )
    else:
        client = Client.find_one({'_id': session.get('client')['_id']})
        info = list([])
        # print('contrats', client['contrats'])
        for cont in client['contratsV']:
            cnt = Contrat_voiture.find_one({'_id': cont})

            print('cnt', cnt['_id'])
            if 'paid' in cnt:
                paid = True
            else:
                paid = False
            void = Garantie.find_one({'_id': session.get('garid')})['voiture_id']
            voit = Voiture.find_one({'_id': void})
            voiture = voit['marq_model'] + " " + voit['matricule']
            vhc = {
                'car': voiture,
                'paid': paid
            }
            info.append(vhc)
        return render_template("resultat/multiple.html", voitures=info, lang=lang)


@app.route('/confirm_email_v/<token>/<lang>')
def confirm_email_v(token, lang):
    if lang == 'french':
        token_expired = u"Votre confirmation est expirée!"
        token_match_err = "Votre confirmation n'est pas compatible!"
        session_err = "Vous devez ouvrir la page dans la même fenêtre"
        msg = u"Votre email est maintenant confirmé, veuillez continuer votre formulaire!"

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
                return render_template('confirm/confirmv.html', confirmed=False, error="not the same email address")
            session.get('client')['confirmed'] = True
        except:
            return render_template('confirm/confirmv.html', confirmed=False, error=session_err)
    except SignatureExpired:
        return render_template('confirm/confirmv.html', confirmed=False, error=token_expired)
    except BadTimeSignature:
        return render_template('confirm/confirmv.html', confirmed=False, error=token_match_err)
    return render_template('confirm/confirmv.html', confirmed=True, success=msg, lang=lang, href="/voiture/10/" + lang)


@app.route("/vars_voiture", methods=['POST'])
def variableV():
    car_damaged = int(request.form['car_damaged'])
    medical = int(request.form['medical'])

    # clmail = session.get('client')['email']
    # client_id = Client.find_one({'email': clmail})['_id']
    # contratv = Contrat_voiture.find({'client_id': client_id})
    # print(contratv)
    contratv = Contrat_voiture.find_one({'_id': session.get('contv_id')})
    conid = session.get('contv_id')

    garid = Contrat_voiture.find_one({'_id': conid})['garantie_id']
    Garantie.update_one(
        {'_id': garid},
        {'$set': {'dommage_suite_aux_cn': car_damaged}}
    )
    Garantie.update_one(
        {'_id': garid},
        {'$set': {'frais_medicaux': medical}}
    )
    Contrat_voiture.update_one(
        {'_id': conid},
        {'$unset': {'coveragev': ""}}
    )
    Contrat_voiture.update_one(
        {'_id': conid},
        {'$unset': {'year_price': ""}}
    )
    Contrat_voiture.update_one(
        {'_id': conid},
        {'$unset': {'year_discount': ""}}
    )
    Contrat_voiture.update_one(
        {'_id': conid},
        {'$unset': {'month_price': ""}}
    )

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
        ['Capital Assure conducteurplus', Garantie.find_one({'_id': garid})['capital_assure_cp']],
        ['Dommage suite aux C.N' , car_damaged],
        ['Frais Med', medical]]


    tab = list([])

    Contrat_voiture.update_one(
        {'_id': conid},
        {'$set': {'coveragev': tab}}
    )
    year_price = 0

    for val in list_garantie:

        price = 0

        if val[0] == "Incendie/Vol":
            price = int(val[1]) * 0.005

        elif val[0] == "Dommage Collision" and val[1] != "EXCLUE":
            price = int(val[1]) * 0.1

        elif val[0] == "Dommage Tous Risque" and val[1] != "EXCLUE":
            price = int(val[1]) * 0.02453
        elif val[0] == "Radio Cassette" and val[1] != "EXCLUE":
            price = int(val[1]) * 0.07
        elif val[0] == "Bris de Glace" and val[1] != "EXCLUE":
            price = int(val[1]) * 0.07
        elif val[0] == "Capital Deces" and val[1] != "EXCLUE":
            price = int(val[1]) * 0.0016
        elif val[0] == "Capital Assure conducteurplus" and val[1] != "EXCLUE":
            price = int(val[1]) * 0.001
        elif val[0] == 'Dommage suite aux C.N':
            price = car_damaged * 0.0065
        elif val[0] == 'Frais Med':
            price = medical * 0.024
        year_price += round(price, 1)
        tab.append({
            'libelle': val[0],
            'valeur': val[1],
            'valeurEstimee': round(price, 1)
        })
        Contrat_voiture.update_one(
                {'_id': conid},
                {'$set': {'coveragev': tab}}
            )

    month_price = round(year_price/12, 1)
    year_discount = round((year_price*5)/100, 1)

    session['price_voiture'] = {
        'year_price': round(year_price - year_discount, 1),
        'month_price': round(month_price, 1)
    }
    if 'year_price' not in Contrat_voiture.find_one({'_id': conid}):
        Contrat_voiture.update_one({'_id': conid}, {'$set': {'year_price': year_price}})
    if 'year_discount' not in Contrat_voiture.find_one({'_id': conid}):
        Contrat_voiture.update_one({'_id': conid}, {'$set': {'year_discount': year_discount}})
    if 'month_price' not in Contrat_voiture.find_one({'_id': conid}):
        Contrat_voiture.update_one({'_id': conid}, {'$set': {'month_price': month_price}})
    return jsonify({
        'month_price': month_price,
        'year_price': year_price,
        'year_discount': year_discount
    })


@app.route('/pay_voiture/<lang>', methods=['POST'])
def payV(lang):
    print('fsjgnsdfgndljkfhglksjdbgjkldsbgslkjdf')
    if request.method == 'POST':
        req = request.form
        card_num = req.get('card_num')
        date_exp = req.get('date_carte')
        cvc = req.get('cvc')
        try:
            datetime.datetime.strptime(date_exp, '%d/%m/%Y')
        except ValueError:
            return redirect('/previewvoiture/' + lang)
        if len(cvc) != 3 or len(card_num) != 16:
            return redirect('/previewvoiture/' + lang)
        client = session.get('client')
        text_societe = "this is the contract of the client : " + client['prenom'] + ' ' + client[
            'nom'] + " with the id " \
                       + str(session.get('client_id')) + " : <br>this contract is paid"
        text_client = "you have just paid your contract for"  # +str(session.get('price_voiture')['year_price'])
        garantie = Garantie.find_one({'_id': session.get('garid')})
        contratv = Contrat_voiture.find_one({'_id': session.get('contv_id')})
        print('beyaaaaaaa')
        print(contratv)
        rendered = render_template('contrat_voiture/contrat_voiture.html',
                                   client=client,
                                   garantie=garantie,
                                   contratv=contratv)
        css = ['./templates/contrat/contrat.css', './templates/contrat/bootstrap.min.css']
        pdf = pdfkit.from_string(rendered, False, css=css)
        sendPDF(client['email'], pdf, text_client, 'voiture')
        sendPDF('henimaher@gmail.com', pdf, text_societe, 'voiture')
        sendPDF('kallel.beya@gmail.com', pdf, text_societe, 'voiture')
        Contrat_voiture.update_one({'_id': session.get('contv_id') },{"$set": {'paid': True}})
        session['done'] = True
        session['client'] = client
        session['void'] = 'multiple'
        session['voiture'] = 'multiple'
        session['contrat'] = 'multiple'
        session['finished'] = True
    return redirect("/previewvoiture/" + lang)


from flask import make_response


@app.route('/gen/contract/voiture')
def generatevoiture():
    print('fgr')
    client = session.get('client')
    garantie = session.get('garantie')
    contratv = Contrat_voiture({'_id': session.get('contv_id')})
    rendered = render_template('contrat_voiture/contrat_voiture.html',
                               client=client,
                               garantie=garantie,
                               contratv=contratv)
    css = ['./templates/contrat/contrat.css', './templates/contrat/bootstrap.min.css']
    pdf = pdfkit.from_string(rendered, False, css=css)

    sendPDF('zied.kanoun6@gmail.com', pdf, 'test pdf 12 12 12', 'voiture')
    sendPDF('henimaher@gmail.com', pdf, 'test pdf 12 12 12', 'voiture')
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = "inline; filename=output.pdf"
    return response


############### end of 5edma ##############
############### 5edmet bouali #############
from PyPDF2 import PdfFileReader, PdfFileWriter, PdfFileMerger

d = dict(
    zip(['vie0', 'vie1', 'vie2', 'vie22', 'vie3', 'vie33', 'vie333', 'vie4', 'vie44', 'vie5', 'vie55', 'vie6'],
        [False for i in range(12)]))


def session_lang():
    try:
        if not (request.args.get('lang')):
            raise Exception()
        session['lang'] = request.args.get('lang')
    except:
        if 'lang' not in session:
            session['lang'] = 'ar'


@app.route("/vie/", methods=['POST', 'GET'])
def home1():
    session_lang()
    error = ''
    if request.method == 'POST':
        fn = request.form.get('first_name')
        ln = request.form.get('last_name')
        # session['fn'] = fn
        # session['ln'] = ln
        session['client'] = Client_(fn, ln).__dict__
        if (fn and ln) and not (fn.isnumeric() and ln.isnumeric()):
            session['vie0'] = True
            return redirect(url_for("vie1"))
        else:
            error = {'fr': 'Le nom doit être non vide et ne doit pas contenir que des chiffres',
                     'en': 'Name is non-empty string with letters', 'ar': 'لا تترك الحقل فارغاً و أدخل حروف'}
    for key in d:
        session[key] = d[key]
    return render_template('vie/sign.html', lang=session['lang'], error=error)



@app.route('/vie/1/', methods=['POST', 'GET'])
def vie1():
    session_lang()
    error = ''
    cursor = mongo.db['Adresse'].find({})
    # print(cursor)
    data = list([])
    # print(mongo.db['Adresse'].count_documents({}))
    for v in cursor:
        data.append(v['adresse'] + ' ' + v['code_postal'])
    if request.method == 'POST':
        session['adresse'] = request.form.get('adresse') + ' '
        session['code'] = session["adresse"][-5:-1]
        if session['adresse'] and session['code'].isnumeric():
            session['vie1'] = True
            return redirect(url_for("vie2"))
        else:
            error = {'fr': u"L'adresse doit être non vide et le code numérique!",
                     'en': 'Enter a non void adress and a number for the code',
                     'ar': "أدخل عنوان و رمز رقمي"}
    if not (session['vie0']):
        return redirect(url_for("home1"))
    return render_template('vie/vie1.html', lang=session['lang'], data=data, error=error)


@app.route('/vie/2/', methods=['POST', 'GET'])
def vie2():
    session_lang()
    erreur = ''
    if request.method == 'POST' and session['vie1']:
        age = request.form.get('age')
        if age.isnumeric() and int(age) > 0 and int(age) < 100:
            session['age'] = age
            session['vie2'] = True
            return redirect(url_for("vie22"))
        else:
            erreur = {'fr': "L'age doit être une valeur numerique entre 0 et 100",
                      'en': "Enter a number between 0 and 100", 'ar': "أدخل رقما بين 0 و 100"}
    if not (session['vie1']):
        return redirect(url_for("vie1"))
    return render_template('vie/vie2.html', lang=session['lang'], error=erreur)


@app.route('/vie/22/', methods=['POST', 'GET'])
def vie22():
    session_lang()
    error = ''
    if request.method == 'POST' and session['vie2']:
        session['sex'] = request.form.get('sex')
        if session['sex']:
            session['vie22'] = True
            return redirect(url_for("vie3"))
        else:
            error = {'fr': "", 'en': "", 'ar': ""}
    if not (session['vie2']):
        return redirect(url_for("vie2"))
    return render_template('vie/vie22.html', lang=session['lang'])


@app.route('/vie/3/', methods=['POST', 'GET'])
def vie3():
    session_lang()
    error = ""
    if request.method == 'POST' and session['vie22']:
        session['w'] = request.form.get('w')
        session['h'] = request.form.get('h')

        if session['w'].isnumeric() and 15 < int(session['w']) < 300 and session['h'].isnumeric() and 15 < int(
                session['h']) < 300:
            session['vie3'] = True
            session['bmi'] = float(session['w']) / (float(session['h']) / 100) * (float(session['h']) / 100)
            return redirect(url_for('vie33'))
        else:
            error = {'fr': "Taper votre taille (30 cm à 300cm) et votre poids (54 à 300kg)",
                     'en': 'Provide height (30-300cm) and wieght (5-300kg)',
                     'ar': 'أدخل طولك(30-cm300) و وزنك(5-kg300)'}
    if not (session['vie22']):
        return redirect(url_for("vie22"))
    return render_template('vie/vie3.html', lang=session['lang'], error=error)


@app.route('/vie/33/', methods=['POST', 'GET'])
def vie33():
    session_lang()
    if request.method == 'POST' and session['vie3']:
        session['smoke'] = request.form.get('smoke')
        if session['smoke']:
            session['vie33'] = True
            return redirect(url_for('vie333'))
    if not (session['vie3']):
        return redirect(url_for("vie3"))
    return render_template('vie/vie33.html', lang=session['lang'])


@app.route('/vie/333/', methods=['POST', 'GET'])
def vie333():
    session_lang()
    if request.method == 'POST' and session['vie33']:
        session['drink'] = request.form.get('drink')
        if session['drink']:
            session['vie333'] = True
            return redirect(url_for('vie4'))
    if not (session['vie33']):
        return redirect(url_for("vie33"))
    return render_template('vie/vie333.html', lang=session['lang'])


@app.route('/vie/4/', methods=['POST', 'GET'])
def vie4():
    session_lang()
    error = ''
    if request.method == 'POST' and session['vie333']:
        session['status'] = request.form.get('status')
        print(session["status"])
        print(session['status'] == 'Célibataire')
        if session['status']:
            session['vie4'] = True
            session['children'] = 0
            session['vie44'] = True
            if session['status'] == 'Célibataire':
                return render_template('vie/vie5.html', lang=session['lang'], skipback=True)
            return redirect(url_for('vie44'))
        else:
            error = {'fr': 'Selectionnez une option', 'en': 'Select an option', 'ar': 'إختر من القائمة'}
    if not (session['vie333']):
        return redirect(url_for("vie333"))
    return render_template('vie/vie4.html', lang=session['lang'], error=error)


@app.route('/vie/44/', methods=['POST', 'GET'])
def vie44():
    session_lang()
    error = ''
    if request.method == 'POST' and session['vie4']:
        session['children'] = request.form.get('children')
        if session['children'].isnumeric() and int(session['children']) <= 10:
            session['vie44'] = True
            return redirect(url_for('vie5'))
        else:
            error = {"fr": "Taper un entier positif ou nul inférieur à 10",
                     "en": "Type a positif or null integer less than 10", "ar": "أدخل رقما موجب أصغر من 10"}
    if not (session['vie4']):
        return redirect(url_for("vie4"))
    return render_template('vie/vie44.html', lang=session['lang'], error=error)


@app.route('/vie/5/', methods=['POST', 'GET'])
def vie5():
    session_lang()
    error = ''
    if request.method == 'POST' and session['vie44']:
        session['salary'] = request.form.get('salary')
        if session['salary'].isnumeric() and int(session['salary']) >= 5000:
            session['vie5'] = True
            return redirect(url_for('vie55'))
        else:
            error = {"fr": "Taper un entier supérieur à 5000 ( 420 par mois)",
                     "en": "Type a positif integer greater than 5000(420 per month)",
                     "ar": "أدخل رقما أكبر أو يساوي 5000(420 فالشهر)"}

    if not (session['vie44']):
        return redirect(url_for("vie44"))
    if session['status'] == 'Célibataire':
        return render_template('vie/vie5.html', lang=session['lang'], error=error, skipback=True)
    return render_template('vie/vie5.html', lang=session['lang'], error=error)


@app.route('/vie/55/', methods=['POST', 'GET'])
def vie55():
    session_lang()
    error = ''
    if request.method == 'POST' and session['vie5']:
        session['debt'] = request.form.get('debt')
        if session['debt'].isnumeric():
            session['vie55'] = True
            return redirect(url_for('vie6'))
        else:
            error = {"fr": "Taper un entier positif ou nul", "en": "Type a positif or null integer",
                     "ar": "أدخل رقما أكبر أو يساوي صفر"}

    if not (session['vie5']):
        return redirect(url_for("vie5"))
    return render_template('vie/vie55.html', lang=session['lang'], error=error)


@app.route('/vie/6/', methods=['POST', 'GET'])
def vie6():
    session_lang()
    error = ''
    if request.method == 'POST' and session['vie55']:
        f = request.files['file']
        print(f.name)
        string = str(uuid.uuid4())
        session['file'] = 'pdfs/' + string[0:7] + '.pdf'
        print("    valhalla                                         ", session['file'])
        f.save("pdfs/{}.pdf".format(string[0:7]))
        try:
            PdfFileReader(open(f'pdfs/{string[0:7]}.pdf', "rb"))
            print("VALID PDF FILE")
        except:
            print("invalid PDF file")
            error = {'fr': 'Ajouter un fichier PDF', 'en': 'Upload a PDF file', 'ar': 'قم بتحميل ملف PDF'}
            return render_template('vie/vie6.html', lang=session['lang'], error=error)

        if f:
            session['vie'] = True
            return redirect('/vie/7/7')
            # return redirect(url_for('result', lang=session['lang']))
    if not (session['vie55']):
        return redirect(url_for("vie55"))
    return render_template('vie/vie6.html', lang=session['lang'], error=error)


@app.route('/vie/7/<nbr>/', methods=['POST', 'GET'])
def vie7(nbr):
    session_lang()
    lang = session['lang']
    error = ''
    if lang == 'fr':
        champerr = u'les champs sont vides!'
        pwderr = u"votre mot de passe n'est pas le méme!"
        pwdregex = u"mot de passe doit avoir une lettre miniscule, une lettre majuscule, un chiffre, et l'un des " \
                   u"charactéres suivants @#$%^&+= "
        verify = u"Nous vous avons envoyé un mail pour confirmer votre adresse email !"
        emailexisterr = u"Cet email est déja dans la base de données veuillez saisir un autre email!"
    elif lang == 'en':
        champerr = 'fields are empty!'
        pwderr = "your password doesn't match!"
        pwdregex = "your password must have a miniscule letter, a capital letter, a number, and one of the following " \
                   "characters @#$%^&+="
        verify = "We've sent you a verification mail for your email address !"
        emailexisterr = "This email is already in data base please type another email!"
    else:
        champerr = 'الرجاء ملء جميع المعطيات'

        pwderr = "كلمة المرور الخاصة بك لا تتطابق!"
        pwdregex = "يجب أن تحتوي كلمة المرور على الأقل على حرف صغير[a .. z]، حرف كبير[A .. Z]، رقم، واحد من الرموز التالية @#$%^&+="
        verify = "!لقد أرسلنا لك بريد التحقق من عنوان البريد الإلكتروني الخاص بك"
        emailexisterr = "!هذا البريد الإلكتروني موجود في قاعدة البيانات، الرجاء كتابة بريد إلكتروني آخر"
    req = request.form
    if int(nbr) == 10:
        if request.method == 'POST' and 'vie9form' in session:
            dbclient = Client.find_one({
                'email': session.get('client')['email'],
            })
            if dbclient is None:
                client = Client.insert_one(
                    session['client']
                )
                client_id = client.inserted_id
            else:
                client = dbclient
                client_id = client['_id']
            client = Client.find_one({'_id': client_id})
            sant = Sante.insert_one({
                'adresse': session['adresse'],
                 'code': session['code'],
                 'sex': session['sex'],
                 'age': session['age'],
                 'bmi': session['bmi'],
                 'smoke': session['smoke'],
                 'drink': session['drink'],
                 'status': session['status'],
                 'children': session['children'],
                 'salary': session['salary'],
                 'debt': session['debt'],
                 'file': session['file']
            })
            cnt_v = Contrat_vie.insert_one({
                    'clent_id': client_id,
                    'sante_id': sant.inserted_id,
                    'name': session['file'][5:len(session['file'])],
                    'date': datetime.datetime.now(),
                    'prix': formule(int(session['salary']), int(session['debt']), int(session['age']))
                })
            Sante.update_one({'_id': sant.inserted_id},{'$set': {'contrat_id': cnt_v.inserted_id}})
            if 'contratsVie' in client:
                contab = client['contratsVie']
                contab.append(cnt_v.inserted_id)
            else :
                contab = list([cnt_v.inserted_id])
            Client.update_one({'_id': client_id}, {'$set': {'contratsVie': contab}})
            session['client_id_vie'] = client_id
            print(session['adresse'])
            return redirect(url_for('result', lang=session['lang']))
        else:
            abort(403)
    if 'vie7' in req:
        email = req.get('email')
        if email == "":
            # # print(email, 'none ')
            return render_template("vie/vie7.html", nbr=7, lang=session['lang'],
                                   error=champerr)
        session.get('client')['email'] = email
        client = session.get('client')
        if mongo.db.clients.find_one({'email': client['email']}):  # client already in data base
            return render_template("vie/vie7.html", nbr=7, lang=session['lang'],
                                   error=emailexisterr)
        token = s.dumps(email, salt='email-confirm')
        link = url_for('confirm_email', lang=session['lang'], token=token, _external=True)
        sendConfirm(email, link)
        session['vie7form'] = 'submitted'
        return render_template('confirm/confirmvie.html', confirmed=False, error=verify, lang=session['lang'])
    if 'vie7b' in req:
        pwderror = ''
        mailerr = ''
        error = ''
        champerr = ''
        recaptchaerr = ''
        if lang == 'fr':
            pwderror = 'Verifiez votre mot de passe !'
            mailerr = 'Verifiez votre email !'
            recaptchaerr = "Veuillez confirmer que vous n'êtes pas un robot!"
            champerr = 'les champs sont vides!'
        if lang == 'en':
            pwderror = 'Verify your password ! '
            mailerr = 'Verify your email !'
            recaptchaerr = "Please confirm that you're not a robot!"
            champerr = 'fields are empty!'
        if lang == 'ar':
            pwderror = '!التحقق من كلمة المرور'
            mailerr = '!تحقق من بريدك الإلكتروني'
            recaptchaerr = "!الرجاء التأكد من أنك لست آلة"
            champerr = 'الرجاء ملء جميع المعطيات'
        if req.get('email') != '':
            client = Client.find_one({'email': req['email']})
            if client:
                session['clid'] = client['_id']
                a = verify_password(client['password'], req.get('password'))
                if a:
                    pwd = req.get('password')
                    if recaptcha.verify():
                        session['client'] = client
                        session['vie7form'] = 'submitted'
                        session['vie8form'] = 'submitted'
                        session['vie9form'] = 'submitted'
                        return redirect('/vie/7/10/', code=307)
                    else:
                        print('recaptcha')
                        error = recaptchaerr
                else:
                    error = pwderror
            else:
                error = mailerr
        else:
            error = champerr
        if error != '':
            return render_template("vie/vie7.html", lang=lang, error=error)
    if 'vie8' in req:
        if 'vie7form' not in session:
            return render_template('vie/vie7.html', lang=lang)
        pwd = req.get('password')
        cpwd = req.get('confirm-password')
        if pwd != cpwd:
            return render_template("vie/vie8.html", nbr=8, lang=lang,
                                   error=pwderr)
        import re
        pattern = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
        password = pwd
        result = re.findall(pattern, password)
        if not result:
            return render_template("vie/vie8.html", nbr=8, lang=lang,
                                   error=pwdregex)
        session.get('client')['password'] = hash_password(pwd)
        session['vie8form'] = 'submitted'
        data = list([])
        cursor = Adresse.find({})
        for doc in cursor:  # préparer les adresses de la bd pour la template
            data.append(doc['adresse'])
        return render_template('vie/vie9.html', lang=lang, data=data)
    if 'vie9' in req:
        if 'vie8form' not in session:
            return render_template('vie/vie8.html', lang=lang)
        tel = req.get('tel')
        cin = req.get('cin')
        birth = req.get('birth')
        adresse = req.get('adresse')
        rue = req.get('rue')
        aptunit = req.get('apt-unit')
        data = list([])
        cursor = Adresse.find({})
        for doc in cursor:  # préparer les adresses de la bd pour la template
            data.append(doc['adresse'])
        if birth == "" or tel == "" or cin == "" or adresse == "" or rue == "" or aptunit == "":
            return render_template("vie/vie9.html", nbr=9, lang=lang,
                                   data=data,
                                   error=champerr)
        tab = adresse.split(',')
        if len(tab) != 3:
            return render_template("vie/vie9.html", nbr=9, lang=lang,
                                   data=data,
                                   error='address not in data base!')
        adresseObj = Adresse.find_one(
            {
                'adresse': adresse
            }
        )
        if adresseObj is None:
            return render_template("vie/vie9.html", nbr=9, lang=lang,
                                   data=data,
                                   error='address not in data base!')
        session.get('client')['date_de_naissance'] = birth
        session.get('client')['tel_num'] = tel
        session.get('client')['cin'] = cin
        session.get('client')['adresse'] = aptunit + ' ' + rue + ', ' + adresse
        session.get('client')['code-postal'] = Adresse.find_one({'adresse': adresse})['code_postal']
        session['vie9form'] = 'submitted'
        return redirect('/vie/7/10/', code=307)
    data = list([])
    cursor = Adresse.find({})
    for doc in cursor:  # préparer les adresses de la bd pour la template
        data.append(doc['adresse'])
    if int(nbr) == 7: return render_template('vie/vie7.html', lang=lang, error=error)
    if int(nbr) == 8: return render_template('vie/vie8.html', lang=lang, error=error)
    if int(nbr) == 9: return render_template('vie/vie9.html', lang=lang, data=data, error=error)
    return render_template('vie/vie6.html', lang=session['lang'], error=error)


def isvalid(card_num, date_exp, cvc):
    try:
        datetime.datetime.strptime(date_exp, '%d/%m/%Y')
    except ValueError:
        return False
    if len(cvc) != 3 or len(card_num) != 16:
        return False
    return True


@app.route("/result/<lang>", methods=['POST', 'GET'])
def result(lang):
    error = ''
    price = formule(int(session['salary']), int(session['debt']), int(session['age']))
    print(price)
    if request.method == 'POST':
        if isvalid(request.form['card_num'], request.form['date_carte'], request.form['cvc']):
            return redirect(url_for("generatevie"))
        else:
            error = {'fr': 'Entrez des données valides', 'en': 'Provide valid card info', 'ar': 'أدخل معطيات حقيقية'}
            return render_template("resultat/preview-vie.html", lang=lang, adresse=session['adresse'], price=price,
                                   error=error)

    return render_template("resultat/preview-vie.html", lang=lang, adresse=session['adresse'], price=price, error=error)


def formule(x, y, z):
    return round(((0.1 * x - 0.01 * y) * (1 + 0.001 * (100 - z))) / 33, 2)


@app.route('/gen/contract/vie')
def generatevie():
    info = [
        ['BMI', session['bmi']],
        ['Fumeur', session['smoke']],
        ['Alcool', session['drink']],
        ['Statut familial', session['status']],
        ["Nombre d'enfants", session['children']]
    ]
    css = ['./templates/contrat/contrat.css', './templates/contrat/bootstrap.min.css']
    print(session['adresse'])
    print(session['sex'])
    rendered = render_template('contrat-vie/contrat.html',
                               fn=session['client']['prenom'],
                               ln=session['client']['nom'],
                               adress=session['adresse'],
                               sex=session['sex'],
                               age=session['age'],
                               somme=formule(int(session['salary']), int(session['debt']), int(session['age'])),
                               dateb=datetime.datetime.now().date(),
                               contrat=0,
                               info=info)
    pdf = pdfkit.from_string(rendered, False, css=css)
    print(f'name: {type(pdf)}')

    r = PdfFileReader(session['file'])
    print(session['file'])
    w = PdfFileWriter()
    with open("templates/contrat-vie/outputtt.pdf", "wb") as f:
        f.write(pdf)

    merger = PdfFileMerger()
    merger.append(open("templates/contrat-vie/outputtt.pdf", "rb"), import_bookmarks=False)
    merger.append(open(session['file'], "rb"), import_bookmarks=False)
    merger.write("contrat.pdf")
    merger.close()
    text_client = "the contract is ready now and waiting to be paid!<br> if you want to modify it just log in and choose" \
                  " your contract if you have more than one"
    text_societe = "this is the contract of the client : " + session['client']['prenom'] + ' ' + session['client']['nom'] + " with the id " \
                   + str(session['client_id_vie']) + " : <br>this contract is paid"
    client = dict()
    client = session.get('client')
    with open('contrat.pdf', "rb") as attachment:
        sendPDF(client['email'], attachment.read(), text_client, 'vie')
        sendPDF('henimaher@gmail.com', attachment.read(), text_societe, 'vie')
    return send_file('contrat.pdf',
                     mimetype='application/pdf', )


############### end of 5edma ##############
############### 5edmet jaabiri ##############
# ------------------------------------------el route mta3 constat add ahbet lel e5er ---------------------------------------------------
@app.route("/addreport/<nbr>/<lang>",methods=["POST","GET"])
def addreport(nbr,lang):
    if lang == 'english':
        adrnotfound = "Your address is not registered in the database!"
        chooseerr="choose an option please !"
        champerr = 'fields are empty!'
        witnesserr='do not add witness without full informations'
        greenerr='enter green card or contract please'
        contacterr='enter atleast one contact information'
    elif lang =='arabe':
        adrnotfound = "عنوانك غير مسجل في قاعدة البيانات!"
        chooseerr = "لازم تختار!"
        champerr = 'البلايص فارغين'
        witnesserr='لا تضيف شاهد بدون معلومات كاملة'
        greenerr='أدخل البطاقة الخضراء أو العقد من فضلك'
        contacterr='حط حاجة نكنتاكتيوك/نكنتاكتيوه عليها'
    else:
        adrnotfound = u"Votre adresse n'est pas enregistrée dans la base de données!"
        chooseerr="choisissez une option s'il vous plaît!"
        champerr = 'les champs sont vides!'
        witnesserr=u'ne pas ajouter de témoin sans informations complètes'
        greenerr="entrez LaCarteVerte Ou Le Contrat S'il Vous Plaît"
        contacterr='entrez au moins une information de contact '
    completed = False
    req = request.form
    data = list([])
    cursor = Adresse.find({})
    for doc in cursor:  # préparer les adresses de la bd pour la template
        data.append(doc['adresse'])
    if request.method == "POST":
        if 'form101' in req:
            acctype = req.get('type')
            if acctype==None:
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=chooseerr)
            if acctype not in ['one', 'two', None]:
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error="don't change values please!")
            session["acctype"]= acctype
            session['form101'] = 'submitted'
        if 'form102' in req:
            date = req.get('date')
            time = req.get('time')
            if time=="" or date=="":
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=champerr)
            session["date"]= date
            session["time"]= time
            session['form102'] = 'submitted'
        if 'form103' in req:
            adresse=req.get('adresse')
            street=req.get('street')
            if adresse=="" or street=="":
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=champerr,data=data)
            adresseObj = Adresse.find_one(
                {
                    'adresse': adresse
                }
            )
            if adresseObj is None:
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       data=data,
                                       error=adrnotfound)
            session["adress_a"] = adresse+','+street
            session['form103'] = 'submitted'
        if 'form104' in req:
            injury = req.get('injury')
            if injury not in ['yes', 'no', None]:
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error="don't change values please!")
            if injury == None:
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=chooseerr)
            session["injury"] = injury
            session['form104'] = 'submitted'
        if 'form105' in req:
            damageov = req.get('damageov')
            if damageov not in ['yes', 'no', None]:
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error="don't change values please!")
            if damageov == None:
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=chooseerr)
            session["damageov"] = damageov
            session['form105'] = 'submitted'
        if 'form106' in req:
            damageob = req.get('damageob')
            if damageob not in ['yes', 'no', None]:
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error="don't change values please!")
            if damageob == None:
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=chooseerr)
            session["damageob"] = damageob
            session['form106'] = 'submitted'
        if 'form107' in req:
            i = 1
            while req.get('namew'+str(int(i))):
                if (req.get('namew'+str(int(i))))=="" or (req.get('telw'+str(int(i))))=="":
                    break
                iv =str(int(i))
                session["namew"+iv]=req.get('namew'+iv)
                session["telw"+iv]=req.get('telw'+iv)
                i += 1
            if (req.get('namew'+str(int(i))))=="" or (req.get('telw'+str(int(i))))=="":
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=witnesserr)
            session['form107'] = 'submitted'
        if 'form108' in req:
            vehicles = Voiture.find({
                "client_id":session["clid"]
            })
            typev_a = req.get('typev')
            brandv_a = req.get('brand')
            typeim = req.get('typeim')
            matriculev_a = req.get('matricule')
            countryv_a = req.get('countryv')
            if typev_a =="normalv":
                if brandv_a=="" or matriculev_a=="" or countryv_a=="":
                    return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                           vehicles=vehicles,error=champerr)
            else:
                if matriculev_a=="" or countryv_a=="":
                    return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                           vehicles=vehicles,error=champerr)
            if typeim=="tunis":
                nserie = req.get('matricule_s')
                if nserie=="":
                    return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                           vehicles=vehicles,error=champerr)
                session["matriculev_a"]= nserie+typeim+matriculev_a
            else:
                session["matriculev_a"] =typeim+':'+matriculev_a      
            session["countryv_a"] = countryv_a
            session["typev_a"] = typev_a
            session["brandv_a"] = brandv_a
            session['form108'] = 'submitted'
        if 'form108b' in req:
            vehicle_id=req.get('cars')
            vehicles = Voiture.find({
                "client_id":session["clid"]
            })
            if vehicle_id==None:
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       vehicles=vehicles,error=champerr)
            vehicle=Voiture.find_one({"_id":ObjectId(vehicle_id)})
            session["vehicle_id"]=ObjectId(vehicle_id)
            session["matriculev_a"] = vehicle['matricule']
            session["countryv_a"] = "tunisia"
            session["typev_a"] = "normalv"
            session["brandv_a"] = vehicle['marq_model']
            # vehicle A from database-------------------------------------------------------------------------------
            session['form108'] = 'submitted'
        if 'form109' in req:
            names_a = req.get('names')
            nb_contract_a = req.get('nbc')
            nb_greencard_a = req.get('nbcv')
            date_b_a = req.get('datecb')
            date_e_a = req.get('datece')
            typeinsurance_a = req.get('typeinsurance')
            nameag_a = req.get('nameag')
            adressag_a = req.get('adressag')
            adrag_a = req.get('adrag')
            emailag_a = req.get('emailag')
            phoneag_a = req.get('telag')
            if names_a=="" or date_b_a=="" or date_e_a=="" or nameag_a=="" or adressag_a=="" or adrag_a=="":
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=champerr,data=data)
            if nb_contract_a=="" and nb_greencard_a=="":
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=greenerr,data=data)
            if emailag_a=="" and phoneag_a=="":
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=contacterr,data=data)
            adresseObj = Adresse.find_one(
                {
                    'adresse': adressag_a
                }
            )
            if adresseObj is None:
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       data=data,
                                       error=adrnotfound)
            session["names_a"] = names_a
            session["nb_contract_a"] = nb_contract_a
            session["nb_greencard_a"] = nb_greencard_a
            session["date_b_a"] = date_b_a
            session["date_e_a"] = date_e_a
            session["typeinsurance_a"] = typeinsurance_a
            session["nameag_a"] = nameag_a
            session["adressag_a"] = adressag_a
            session["adrag_a"] = adrag_a
            session["emailag_a"] = emailag_a
            session["phoneag_a"] = phoneag_a
            session['form109'] = 'submitted'
        if 'form109b' in req:
            if "vehicle_id" in session:
                garantie = Garantie.find_one({"voiture_id":session["vehicle_id"]})
                contrat = Contrat_voiture.find_one({"_id":garantie['contract']})
                session["nb_contract_a"] = garantie['contract']
                session["date_b_a"] =contrat['date_de_debut_du_contrat']
            else:
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error="you didnt choose a vehicle",data=data)
            # insurance_soc_A from database----------------------------------------------------------------------------------
            session["names_a"] ="constante"
            session["nb_greencard_a"] =""
            session["date_e_a"] =""
            session["typeinsurance_a"] = "agency"
            session["nameag_a"] = "constante"
            session["adressag_a"] ="constante"
            session["adrag_a"] ="constante"
            session["emailag_a"] ="constante"
            session["phoneag_a"] ="constante"
            session['form109'] = 'submitted'
        if 'form110' in req:
            damageins_a = req.get('damageins')
            if damageins_a not in ['yes', 'no', None]:
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error="don't change values please!")
            if damageins_a == None:
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=chooseerr)
            session["damageins_a"]= damageins_a
            session['form110'] = 'submitted'
        if 'form111' in req:
            namedr_a = req.get('full_namedr')
            lnamedr_a = req.get('last_namedr')
            birthdaydr_a = req.get('birthdaydr')
            adressdr_a = req.get('adressdr')
            countrydr_a = req.get('countrydr')
            emaildr_a = req.get('emaildr')
            teldr_a = req.get('teldr')
            permis_a = req.get('permis')
            categoryp_a = req.get('categoryp')
            validp_a = req.get('validp')
            if namedr_a==""or lnamedr_a=="" or birthdaydr_a=="" or adressdr_a=="" or countrydr_a=="" or permis_a=="" or categoryp_a=="" or validp_a=="":
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=champerr,data=data)
            if emaildr_a=="" and teldr_a=="":
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=contacterr,data=data)
            adresseObj = Adresse.find_one(
                {
                    'adresse': adressdr_a
                }
            )
            if adresseObj is None:
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       data=data,
                                       error=adrnotfound)
            session["namedr_a"] = namedr_a
            session["lnamedr_a"] = lnamedr_a
            session["birthdaydr_a"] = birthdaydr_a
            session["adressdr_a"] = adressdr_a
            session["countrydr_a"] = countrydr_a
            session["emaildr_a"] = emaildr_a
            session["teldr_a"] = teldr_a
            session["permis_a"] = permis_a
            session["categoryp_a"] = categoryp_a
            session["validp_a"] = validp_a
            session['form111'] = 'submitted'
        if 'form111b' in req:
            if "clid" in session:
                driver = Client.find_one({"_id": session["clid"]})
                insured_A_adr = driver['adresse']
            else:
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       data=data,
                                       error="you're not connected")
            permis_a = req.get('permis')
            categoryp_a = req.get('categoryp')
            validp_a = req.get('validp')
            if permis_a=="" or categoryp_a=="" or validp_a=="":
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=champerr,data=data)
            session["namedr_a"]= driver['nom']
            session["lnamedr_a"]=driver['prenom']
            session["birthdaydr_a"]= driver['date_de_naissance']
            session["adressdr_a"]=insured_A_adr
            session["countrydr_a"]= "tunisia"
            session["emaildr_a"]= driver['email']
            session["teldr_a"]= driver['tel_num']
            session["permis_a"]=permis_a
            session["categoryp_a"]=categoryp_a
            session["validp_a"]=validp_a
            session['form111']='submitted'
        if 'form112' in req: 
            chocpt_a = req.get('type')
            if chocpt_a == None:
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=chooseerr)
            if chocpt_a not in ['right, left', 'right, middle', 'right, right','left, right','left, middle','left, left'
            ,'front, left','front, middle','front, right','back, left','back, middle','back, right']:
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error="don't change values please!")
            session["chocpt_a"] = chocpt_a
            session['form112'] = 'submitted'
        if 'form113' in req:
            appdamage_a=req.get('appdamage')
            session["appdamage_a"]=appdamage_a
            session['form113'] = 'submitted'
        if 'form114' in req:
            obs_a=req.get('obs')
            session["obs_a"]=obs_a
            session['form114'] = 'submitted'
            if session['acctype'] =="one":
                return redirect("/addreport/23/" + lang)
        if 'form115' in req:
            name_b =req.get('name')
            lname_b=req.get('lname')
            adress_b=req.get('adress')
            rue_b=req.get('rue')
            email_b=req.get('email')
            tel_b=req.get('tel')
            if name_b=="" or lname_b=="" or adress_b=="" or rue_b=="":
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=champerr,data=data)
            if email_b=="" and tel_b=="":
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=contacterr,data=data)
            adresseObj = Adresse.find_one(
                {
                    'adresse': adress_b
                }
            )
            if adresseObj is None:
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       data=data,
                                       error=adrnotfound)
            adresse = Adresse.find_one({'_id': adresseObj['_id']})
            session["name_b"]=name_b
            session["lname_b"]=lname_b
            session["adress_b"]=adress_b+','+rue_b
            session["codep_b"]=adresse['code_postal']
            session["country_b"]='tunisia'
            session["email_b"]=email_b
            session["tel_b"]=tel_b
            session['form115'] = 'submitted'
        if 'form116' in req:
            typev_b = req.get('typev')
            brandv_b = req.get('brand')
            typeim = req.get('typeim')
            matriculev_b = req.get('matricule')
            countryv_b = req.get('countryv')
            if typev_b =="normalv":
                if brandv_b=="" or matriculev_b=="" or countryv_b=="":
                    return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                           error=champerr)
            else:
                if matriculev_b=="" or countryv_b=="":
                    return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                           error=champerr)
            if typeim=="tunis":
                nserie = req.get('matricule_s')
                if nserie=="":
                    return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                           error=champerr)
                session["matriculev_b"]= nserie+typeim+matriculev_b
            else:
                session["matriculev_b"] = typeim+':'+matriculev_b
            session["countryv_b"] = countryv_b
            session["typev_b"] = typev_b
            session["brandv_b"] = brandv_b
            session['form116'] = 'submitted'
        if 'form117' in req:
            names_b = req.get('names')
            nb_contract_b = req.get('nbc')
            nb_greencard_b = req.get('nbcv')
            date_b_b = req.get('datecb')
            date_e_b = req.get('datece')
            typeinsurance_b = req.get('typeinsurance')
            nameag_b = req.get('nameag')
            adressag_b = req.get('adressag')
            adrag_b = req.get('adrag')
            emailag_b = req.get('emailag')
            phoneag_b = req.get('telag')
            if names_b=="" or date_b_b=="" or date_e_b=="" or nameag_b=="" or adressag_b=="" or adrag_b=="":
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=champerr,data=data)
            if nb_contract_b=="" and nb_greencard_b=="":
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=greenerr,data=data)
            if emailag_b=="" and phoneag_b=="":
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=contacterr,data=data)
            adresseObj = Adresse.find_one(
                {
                    'adresse': adressag_b
                }
            )
            if adresseObj is None:
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       data=data,
                                       error=adrnotfound)
            session["names_b"] = names_b
            session["nb_contract_b"] = nb_contract_b
            session["nb_greencard_b"] = nb_greencard_b
            session["date_b_b"] = date_b_b
            session["date_e_b"] = date_e_b
            session["typeinsurance_b"] = typeinsurance_b
            session["nameag_b"] = nameag_b
            session["adressag_b"] = adressag_b
            session["adrag_b"] = adrag_b
            session["emailag_b"] = emailag_b
            session["phoneag_b"] = phoneag_b
            session['form117'] = 'submitted'
        if 'form118' in req:
            damageins_b = req.get('damageins')
            if damageins_b not in ['yes', 'no', None]:
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error="don't change values please!")
            if damageins_b == None:
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=chooseerr)
            session["damageins_b"]= damageins_b
            session['form118'] = 'submitted'
        if 'form119' in req:
            namedr_b = req.get('full_namedr')
            lnamedr_b = req.get('last_namedr')
            birthdaydr_b = req.get('birthdaydr')
            adressdr_b = req.get('adressdr')
            countrydr_b = req.get('countrydr')
            emaildr_b = req.get('emaildr')
            teldr_b = req.get('teldr')
            permis_b = req.get('permis')
            categoryp_b = req.get('categoryp')
            validp_b = req.get('validp')
            if namedr_b=="" or lnamedr_b=="" or birthdaydr_b=="" or adressdr_b=="" or countrydr_b=="" or permis_b=="" or categoryp_b=="" or validp_b=="":
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=champerr,data=data)
            if emaildr_b=="" and teldr_b=="":
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=contacterr,data=data)
            adresseObj = Adresse.find_one(
                {
                    'adresse': adressdr_b
                }
            )
            if adresseObj is None:
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       data=data,
                                       error=adrnotfound)
            session["namedr_b"] = namedr_b
            session["lnamedr_b"] = lnamedr_b
            session["birthdaydr_b"] = birthdaydr_b
            session["adressdr_b"] = adressdr_b
            session["countrydr_b"] = countrydr_b
            session["emaildr_b"] = emaildr_b
            session["teldr_b"] = teldr_b
            session["permis_b"] = permis_b
            session["categoryp_b"] = categoryp_b
            session["validp_b"] = validp_b
            session['form119'] = 'submitted'
        if 'form120' in req:
            chocpt_b = req.get('type')
            if chocpt_b == None:
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=chooseerr)
            if chocpt_b not in ['right, left', 'right, middle', 'right, right','left, right','left, middle','left, left'
            ,'front, left','front, middle','front, right','back, left','back, middle','back, right']:
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error="don't change values please!")
            session["chocpt_b"] = chocpt_b
            session['form120'] = 'submitted'
        if 'form121' in req:
            appdamage_b=req.get('appdamage')
            session["appdamage_b"]=appdamage_b
            session['form121'] = 'submitted'
        if 'form122' in req:
            obs_b=req.get('obs')
            session["obs_b"]=obs_b
            session['form122'] = 'submitted'
        if 'form123' in req:
            circumstances_a=req.getlist('circumstances_a')
            circumstances_b=req.getlist('circumstances_b')
            if len(circumstances_a)==0:
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=champerr,acctype=session.get('acctype'))
            if len(circumstances_b)==0 and session.get('acctype')=="two":
                return render_template("/constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=champerr,acctype=session.get('acctype'))
            session["circumstances_a"]=circumstances_a
            session["circumstances_b"]=circumstances_b
            session['form123'] = 'submitted'
        if 'form124' in req:
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # if user does not select file, browser also
            #  submit an empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                session["accident_sketch"]=filename
                session['form115'] = 'submitted'
                completed=True
    #----------------------------control of access to reports pages----------------------------------------------
    if session.get('acctype')=="one":
        if (int(nbr) in range(2, 15)or(int(nbr)==24)) and ('form' + str(int(nbr)+99) not in session):
            form = "1"
            for k in range(1, 14):
                v=k+100
                if ('form' + str(v)) in session:
                    form = str(k+1)
            for k in range(23, 24):
                v=k+100
                if ('form' + str(v)) in session:
                    form = str(k+1)
            return redirect("/addreport/" + form + "/" + lang)
        if int(nbr) in range(15, 23):
            return redirect("/addreport/1/" + lang)
        if int(nbr)==23 and ('form114' not in session):
            form = "1"
            for k in range(1, 14):
                v=k+100
                if ('form' + str(v)) in session:
                    form = str(k+1)
            return redirect("/addreport/" + form + "/" + lang)
    else:
        if int(nbr) in range(2, 25) and ('form' + str(int(nbr)+99) not in session):
            form = "1"
            for k in range(2, 24):
                v=k+100
                if ('form' + str(v)) in session:
                    form = str(k+1)
            return redirect("/addreport/" + form + "/" + lang)
    #----------------------------end control----------------------------------------------
    if completed:
        j = 1
        # wnames=""
        # wphones=""
        wits=""
        while session.get('namew'+str(int(j))):
            jv=str(int(j))
            # wnames+=session["namew"+jv]+";"
            # wphones+=session["telw"+jv]+";"
            if session.get('namew'+str(int(j+1))):
                wits+=session["namew"+jv]+":"+session["telw"+jv]+";"
            else:
                wits+=session["namew"+jv]+":"+session["telw"+jv]
            j += 1
        curc_a=""
        curc_b=""
        for value in session["circumstances_a"]:
            curc_a+=value+";"
        for value in session["circumstances_b"]:
            curc_b+=value+";"

        if session['acctype']=="one":
            exp = {
                "date":session["date"],
                "time":session["time"],
                "adress":session["adress_a"],
                "injuries":session["injury"],
                "damage_to_other_vehicles":session["damageov"],
                "damage_to_other_objects":session["damageob"],
                "witnesses":wits,
                "insured_A":session["clid"],
                "vehicle_A":{
                    "type":session["typev_a"],
                    "brand":session["brandv_a"],
                    "registration_number":session["matriculev_a"],
                    "country":session["countryv_a"]
                },
                "insurance_society_A":{
                    "name":session["names_a"],
                    "number_of_contract":session["nb_contract_a"],
                    "number_of_greencard":session["nb_greencard_a"],
                    "starting_date":session["date_b_a"],
                    "ending_date":session["date_e_a"],
                    "type_insurance":session["typeinsurance_a"],
                    "name_of_type":session["nameag_a"],
                    "adress":session["adressag_a"]+', '+session["adrag_a"],
                    "email":session["emailag_a"],
                    "phone":session["phoneag_a"],
                    "material_damage_insured":session["damageins_a"]
                },
                "driver_A":{
                    "name":session["namedr_a"],
                    "last_name":session["lnamedr_a"],
                    "birthday":session["birthdaydr_a"],
                    "adress":session["adressdr_a"]+', '+session["countrydr_a"],
                    "email":session["emaildr_a"],
                    "phone":session["teldr_a"],
                    "permis":session["permis_a"],
                    "category":session["categoryp_a"],
                    "available_until":session["validp_a"]
                } ,
                "shock_point_car_A":session["chocpt_a"],
                "damage_apparent_A":session["appdamage_a"],
                "observations_A":session["obs_a"],
                "circumstances_A":curc_a,
                "accident_sketch":session["accident_sketch"]
            }
        else:
            exp = {
                "date":session["date"],
                "time":session["time"],
                "adress":session["adress_a"],
                "injuries":session["injury"],
                "damage_to_other_vehicles":session["damageov"],
                "damage_to_other_objects":session["damageob"],
                "witnesses":wits,
                "insured_A":session["clid"],
                "vehicle_A":{
                    "type":session["typev_a"],
                    "brand":session["brandv_a"],
                    "registration_number":session["matriculev_a"],
                    "country":session["countryv_a"]
                },
                "insurance_society_A":{
                    "name":session["names_a"],
                    "number_of_contract":session["nb_contract_a"],
                    "number_of_greencard":session["nb_greencard_a"],
                    "starting_date":session["date_b_a"],
                    "ending_date":session["date_e_a"],
                    "type_insurance":session["typeinsurance_a"],
                    "name_of_type":session["nameag_a"],
                    "adress":session["adressag_a"]+', '+session["adrag_a"],
                    "email":session["emailag_a"],
                    "phone":session["phoneag_a"],
                    "material_damage_insured":session["damageins_a"]
                },
                "driver_A":{
                    "name":session["namedr_a"],
                    "last_name":session["lnamedr_a"],
                    "birthday":session["birthdaydr_a"],
                    "adress":session["adressdr_a"]+', '+session["countrydr_a"],
                    "email":session["emaildr_a"],
                    "phone":session["teldr_a"],
                    "permis":session["permis_a"],
                    "category":session["categoryp_a"],
                    "available_until":session["validp_a"]
                } ,
                "shock_point_car_A":session["chocpt_a"],
                "damage_apparent_A":session["appdamage_a"],
                "observations_A":session["obs_a"],
                "insured_B":{
                    "name":session["name_b"],
                    "last_name":session["lname_b"],
                    "adress":session["adress_b"]+', '+session["country_b"],
                    "postal_code":session["codep_b"],
                    "email":session["email_b"],
                    "phone":session["tel_b"],
                },
                "vehicle_B":{
                    "type":session["typev_b"],
                    "brand":session["brandv_b"],
                    "registration_number":session["matriculev_b"],
                    "country":session["countryv_b"]
                },
                "insurance_society_B":{
                    "name":session["names_b"],
                    "number_of_contract":session["nb_contract_b"],
                    "number_of_greencard":session["nb_greencard_b"],
                    "starting_date":session["date_b_b"],
                    "ending_date":session["date_e_b"],
                    "type_insurance":session["typeinsurance_b"],
                    "name_of_type":session["nameag_b"],
                    "adress":session["adressag_b"]+', '+session["adrag_b"],
                    "email":session["emailag_b"],
                    "phone":session["phoneag_b"],
                    "material_damage_insured":session["damageins_b"]
                },
                "driver_B":{
                    "name":session["namedr_b"],
                    "last_name":session["lnamedr_b"],
                    "birthday":session["birthdaydr_b"],
                    "adress":session["adressdr_b"]+', '+session["countrydr_b"],
                    "email":session["emaildr_b"],
                    "phone":session["teldr_b"],
                    "permis":session["permis_b"],
                    "category":session["categoryp_b"],
                    "available_until":session["validp_b"]
                },
                "shock_point_car_B":session["chocpt_b"],
                "damage_apparent_B": session["appdamage_b"],
                "observations_B": session["obs_b"],
                "circumstances_A": curc_a,
                "circumstances_B": curc_b,
                "accident_sketch": session["accident_sketch"]
            }
        # ----------------badel el collection bech 7atit--------------------------------------------------------
        report = collection.insert_one(exp)
        session['reportid'] = report.inserted_id
        return redirect(url_for("getit"))
    if nbr == "8":
        if 'clid' not in session:
            return render_template('confirm/login.html', lang=lang, carreport=True)
        vehicles = Voiture.find({
            "client_id": session["clid"]
        })
        return render_template("/constat_form/addreport" + nbr + ".html", lang=lang,
                               nbr=nbr, acctype=session.get('acctype'), data=data, vehicles=vehicles)
    return render_template("/constat_form/addreport" + nbr + ".html", lang=lang,
                           nbr=nbr, acctype=session.get('acctype'), data=data)


# ----------------end-----------------------------------------------------------------------------------
@app.route("/getit/", methods=["GET"])
def getit():
    # path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    # config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    getthat = collection.find_one({"_id": session['reportid']})
    insured_A = Client.find_one({"_id": getthat['insured_A']})
    insured_A_adr = insured_A['adresse']
    insured_A_pos=insured_A['code-postal']
    nbcurc_a = getthat['circumstances_A'].count(";")
    with open('static/public/'+session["accident_sketch"], 'rb') as image_file:
            sketch = base64.b64encode(image_file.read())
            skett = str(sketch)
            ske = skett[2:-1]
    client = session.get('client')
    if session['acctype']=="one":
        rendered = render_template("constat/constat1pdf.html", report=getthat, nba=nbcurc_a,
                                   insured_A=insured_A, ins_A_adr=insured_A_adr, ins_A_pos=insured_A_pos, sketch=ske)
        css = ['./templates/constat/constat.css']
        pdf = pdfkit.from_string(rendered, False, css=css)
        sendPDF(client['email'], pdf, 'Here is your car report', 'car report')
        sendPDF('henimaher@gmail.com', pdf, 'Here is your car report', 'car report')
        return render_template("/constat_form/constatvoitureone.html", report=getthat, nba=nbcurc_a,
                               insured_A=insured_A, ins_A_adr=insured_A_adr, ins_A_pos=insured_A_pos)
    nbcurc_b = getthat['circumstances_B'].count(";")
    rendered = render_template("constat/constat2pdf.html", report=getthat, nba=nbcurc_a, nbb=nbcurc_b,
                               insured_A=insured_A, ins_A_adr=insured_A_adr, ins_A_pos=insured_A_pos)
    css = ['./templates/constat/constat.css']
    pdf = pdfkit.from_string(rendered, False, css=css)
    sendPDF(client['email'], pdf, 'Here is your car report', 'car report')
    sendPDF('henimaher@gmail.com', pdf, 'Here is your car report', 'car report')
    return render_template("/constat_form/constat_voiture.html", report=getthat, nba=nbcurc_a, nbb=nbcurc_b,
                           insured_A=insured_A, ins_A_adr=insured_A_adr, ins_A_pos=insured_A_pos)


# ------------------------------------------------------------------end---------------------------------------------------
############### end of 5edma ##############

if __name__ == '__main__':
    app.run()
