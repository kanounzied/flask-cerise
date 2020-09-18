#-------------------------------------------------------eli ne9es zidou-----------------------------
from flask import Flask, redirect, url_for, render_template, request, session, jsonify,flash
import pymongo
from pymongo import MongoClient
import json
from bson import json_util
from datetime import timedelta
from flask_session import Session
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from flask_assets import Environment, Bundle
from werkzeug.utils import secure_filename
import os.path
#--------------------------------------------------end------------------------------------------------
#--------------------------configmta3 upload file zidha w badel elpath------------------------------
UPLOAD_FOLDER = '/Users/ahmed/Desktop/flaskone/public'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
#-------------------------------end-------------------------------------------------------
#-----------------------------------config el base badlou----------------------
cluster = MongoClient(port=27017)
db = cluster["insurance"]
collection = db["cars_insurance"]
#------------------------------------end-----------------------------------------
app = Flask(__name__)
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
app.config['DEBUG'] = True
#---------------------------------------------kifkif upload--------------------------------
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#-------------------------------------------------end----------------------------------------
#Bootstrap(app)

@app.before_request
def make_session_permanent():  # la session est valide pour seulement une heure
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=60)
#----------------------------------------------------mta3 lfiles w el return mta3 l'ajout zidhom----------------------
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/getit/", methods=["GET"])
def getit():
    getthat = collection.find_one({"_id":session['reportid']})
    print(getthat)
    return json.dumps(getthat, default=json_util.default)
    #  allcars = list(collection.find({}))
    #  return json.dumps(allcars, default=json_util.default)
#------------------------------------------------------------------end-------------------------------------------------------

@app.route("/clear")
def clear():  # vider la session client
    session.clear()
    return "<h1>session cleared"

@app.route("/test/<lang>")
def test(lang):  # vider la session client
    return render_template("test.html",lang=lang)
#----------------------------------------------------el constat ahbet lel e5er ---------------------------------------------------
@app.route("/addreport/<nbr>/<lang>",methods=["POST","GET"])
def addreport(nbr,lang):
    if lang == 'english':
        chooseerr="choose an option please !"
        champerr = 'fields are empty!'
        witnesserr='do not add witness without full informations'
        greenerr='enter green card or contract please'
        contacterr='enter atleast one contact information'
    completed = False
    if request.method == "POST":
        req = request.form
        if 'form101' in req:
            date = req.get('date')
            if date=="":
                return render_template("constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error='enter a date please')
            session["date"]= date
            session['form101'] = 'submitted'
        if 'form102' in req:
            time = req.get('time')
            if time=="":
                return render_template("constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error='enter a time please')
            session["time"]= time
            session['form102'] = 'submitted'
        if 'form103' in req:
            country=req.get('country')
            city=req.get('city')
            street=req.get('street')
            if country=="" or city=="" or street=="":
                return render_template("constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=champerr)
            session["city"] = city
            session["country"] = country
            session["street"] = street
            session['form103'] = 'submitted'
        if 'form104' in req:
            injury = req.get('injury')
            if injury not in ['yes', 'no', None]:
                return render_template("constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error="don't change values please!")
            if injury == None:
                return render_template("constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=chooseerr)
            session["injury"] = injury
            session['form104'] = 'submitted'
        if 'form105' in req:
            damageov = req.get('damageov')
            if damageov not in ['yes', 'no', None]:
                return render_template("constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error="don't change values please!")
            if damageov == None:
                return render_template("constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=chooseerr)
            session["damageov"] = damageov
            session['form105'] = 'submitted'
        if 'form106' in req:
            damageob = req.get('damageob')
            if damageob not in ['yes', 'no', None]:
                return render_template("constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error="don't change values please!")
            if damageob == None:
                return render_template("constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
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
                return render_template("constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=witnesserr)
            session['form107'] = 'submitted'
        if 'form108' in req:
            typev_a = req.get('typev')
            brandv_a = req.get('brand')
            matriculev_a = req.get('matricule')
            countryv_a = req.get('countryv')
            if typev_a =="normalv":
                if brandv_a=="" or matriculev_a=="" or countryv_a=="":
                    return render_template("constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                           error=champerr)
            else:
                if matriculev_a=="" or countryv_a=="":
                    return render_template("constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                           error=champerr)
            session["typev_a"] = typev_a
            session["brandv_a"] = brandv_a
            session["matriculev_a"] = matriculev_a
            session["countryv_a"] = countryv_a
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
            countryag_a = req.get('countryag')
            emailag_a = req.get('emailag')
            phoneag_a = req.get('telag')
            if names_a=="" or date_b_a=="" or date_e_a=="" or nameag_a=="" or adressag_a=="" or countryag_a=="":
                return render_template("constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=champerr)
            if nb_contract_a=="" and nb_greencard_a=="":
                return render_template("constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=greenerr)
            if emailag_a=="" and phoneag_a=="":
                return render_template("constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=contacterr)
            session["names_a"] = names_a
            session["nb_contract_a"] = nb_contract_a
            session["nb_greencard_a"] = nb_greencard_a
            session["date_b_a"] = date_b_a
            session["date_e_a"] = date_e_a
            session["typeinsurance_a"] = typeinsurance_a
            session["nameag_a"] = nameag_a
            session["adressag_a"] = adressag_a
            session["countryag_a"] = countryag_a
            session["emailag_a"] = emailag_a
            session["phoneag_a"] = phoneag_a
            session['form109'] = 'submitted'
        if 'form110' in req:
            damageins_a = req.get('damageins')
            if damageins_a not in ['yes', 'no', None]:
                return render_template("constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error="don't change values please!")
            if damageins_a == None:
                return render_template("constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=chooseerr)
            session["damageins_a"]= damageins_a
            session['form110'] = 'submitted'
        if 'form111' in req:
            namedr_a = req.get('full_namedr')
            birthdaydr_a = req.get('birthdaydr')
            adressdr_a = req.get('adressdr')
            countrydr_a = req.get('countrydr')
            emaildr_a = req.get('emaildr')
            teldr_a = req.get('teldr')
            permis_a = req.get('permis')
            categoryp_a = req.get('categoryp')
            validp_a = req.get('validp')
            if namedr_a=="" or birthdaydr_a=="" or adressdr_a=="" or countrydr_a=="" or permis_a=="" or categoryp_a=="" or validp_a=="":
                return render_template("constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=champerr)
            if emaildr_a=="" and teldr_a=="":
                return render_template("constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=contacterr)
            session["namedr_a"] = namedr_a
            session["birthdaydr_a"] = birthdaydr_a
            session["adressdr_a"] = adressdr_a
            session["countrydr_a"] = countrydr_a
            session["emaildr_a"] = emaildr_a
            session["teldr_a"] = teldr_a
            session["permis_a"] = permis_a
            session["categoryp_a"] = categoryp_a
            session["validp_a"] = validp_a
            session['form111'] = 'submitted'
        if 'form112' in req:
            chocside_a = req.get('chocside')
            chocpt_a = req.get('chocpt')
            session["chocside_a"] = chocside_a
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
        if 'form115' in req:
            name_b =req.get('name')
            adress_b=req.get('adress')
            codep_b=req.get('codep')
            country_b=req.get('country')
            email_b=req.get('email')
            tel_b=req.get('tel')
            if name_b=="" or adress_b=="" or codep_b=="" or country_b=="":
                return render_template("constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=champerr)
            if email_b=="" and tel_b=="":
                return render_template("constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=contacterr)
            session["name_b"]=name_b
            session["adress_b"]=adress_b
            session["codep_b"]=codep_b
            session["country_b"]=country_b
            session["email_b"]=email_b
            session["tel_b"]=tel_b
            session['form115'] = 'submitted'
        if 'form116' in req:
            typev_b = req.get('typev')
            brandv_b = req.get('brand')
            matriculev_b = req.get('matricule')
            countryv_b = req.get('countryv')
            if typev_b =="normalv":
                if brandv_b=="" or matriculev_b=="" or countryv_b=="":
                    return render_template("constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                           error=champerr)
            else:
                if matriculev_b=="" or countryv_b=="":
                    return render_template("constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                           error=champerr)
            session["typev_b"] = typev_b
            session["brandv_b"] = brandv_b
            session["matriculev_b"] = matriculev_b
            session["countryv_b"] = countryv_b
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
            countryag_b = req.get('countryag')
            emailag_b = req.get('emailag')
            phoneag_b = req.get('telag')
            if names_b=="" or date_b_b=="" or date_e_b=="" or nameag_b=="" or adressag_b=="" or countryag_b=="":
                return render_template("constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=champerr)
            if nb_contract_b=="" and nb_greencard_b=="":
                return render_template("constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=greenerr)
            if emailag_b=="" and phoneag_b=="":
                return render_template("constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=contacterr)
            session["names_b"] = names_b
            session["nb_contract_b"] = nb_contract_b
            session["nb_greencard_b"] = nb_greencard_b
            session["date_b_b"] = date_b_b
            session["date_e_b"] = date_e_b
            session["typeinsurance_b"] = typeinsurance_b
            session["nameag_b"] = nameag_b
            session["adressag_b"] = adressag_b
            session["countryag_b"] = countryag_b
            session["emailag_b"] = emailag_b
            session["phoneag_b"] = phoneag_b
            session['form117'] = 'submitted'
        if 'form118' in req:
            damageins_b = req.get('damageins')
            if damageins_b not in ['yes', 'no', None]:
                return render_template("constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error="don't change values please!")
            if damageins_b == None:
                return render_template("constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=chooseerr)
            session["damageins_b"]= damageins_b
            session['form118'] = 'submitted'
        if 'form119' in req:
            namedr_b = req.get('full_namedr')
            birthdaydr_b = req.get('birthdaydr')
            adressdr_b = req.get('adressdr')
            countrydr_b = req.get('countrydr')
            emaildr_b = req.get('emaildr')
            teldr_b = req.get('teldr')
            permis_b = req.get('permis')
            categoryp_b = req.get('categoryp')
            validp_b = req.get('validp')
            if namedr_b=="" or birthdaydr_b=="" or adressdr_b=="" or countrydr_b=="" or permis_b=="" or categoryp_b=="" or validp_b=="":
                return render_template("constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=champerr)
            if emaildr_b=="" and teldr_b=="":
                return render_template("constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=contacterr)
            session["namedr_b"] = namedr_b
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
            chocside_b = req.get('chocside')
            chocpt_b = req.get('chocpt')
            session["chocside_b"] = chocside_b
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
            if circumstances_a=="" or circumstances_b=="":
                return render_template("constat_form/addreport" + str(int(nbr) - 1) + ".html", nbr=int(nbr) - 1, lang=lang,
                                       error=champerr)
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
    if int(nbr) in range(2, 25) and ('form' + str(int(nbr)+99) not in session):
        form = "1"
        for k in range(2, 25):
            v=k+100
            if ('form' + str(v)) in session:
                form = str(k+1)
        return redirect("/addreport/" + form + "/" + lang)
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
        for index,value in enumerate(session["circumstances_a"]):
            if index+1 < len(session["circumstances_a"]):
                curc_a+=value+";"
            else:
                curc_a+=value
        for index,value in enumerate(session["circumstances_b"]):
            if index+1 < len(session["circumstances_b"]):
                curc_b+=value+";"
            else:
                curc_b+=value
        exp = {
            "date":session["date"],
            "time":session["time"],
            "adress":session["country"]+', '+session["city"]+', '+session["street"],
            "injuries":session["injury"],
            "damage_to_other_vehicles":session["damageov"],
            "damage_to_other_objects":session["damageob"],
            "witnesses":wits,
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
                "adress":session["adressag_a"]+', '+session["countryag_a"],
                "e-mail":session["emailag_a"],
                "phone":session["phoneag_a"],
                "material_damage_insured?":session["damageins_a"]
            },
            "driver_A":{
                "name":session["namedr_a"],
                "birthday":session["birthdaydr_a"],
                "adress":session["adressdr_a"]+', '+session["countrydr_a"],
                "e-mail":session["emaildr_a"],
                "phone":session["teldr_a"],
                "permis":session["permis_a"],
                "category":session["categoryp_a"],
                "available_until":session["validp_a"]
            } ,
            "shock_point_car_A":session["chocside_a"]+', '+session["chocpt_a"],
            "damage_apparent_A":session["appdamage_a"],
            "observations_A":session["obs_a"],
            "insured_B":{
                "name":session["name_b"],
                "adress":session["adress_b"]+', '+session["country_b"],
                "postal_code":session["codep_b"],
                "e-mail":session["email_b"],
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
                "adress":session["adressag_b"]+', '+session["countryag_b"],
                "e-mail":session["emailag_b"],
                "phone":session["phoneag_b"],
                "material_damage_insured?":session["damageins_b"]
            },
            "driver_B":{
                "name":session["namedr_b"],
                "birthday":session["birthdaydr_b"],
                "adress":session["adressdr_b"]+', '+session["countrydr_b"],
                "e-mail":session["emaildr_b"],
                "phone":session["teldr_b"],
                "permis":session["permis_b"],
                "category":session["categoryp_b"],
                "available_until":session["validp_b"]
            },
            "shock_point_car_B":session["chocside_b"]+', '+session["chocpt_b"],
            "damage_apparent_B":session["appdamage_b"],
            "observations_B":session["obs_b"],
            "circumstances_A":curc_a,
            "circumstances_B":curc_b,
            "accident_sketch":session["accident_sketch"]
        }
#----------------mazel ellouta ama lahne bech tbadel el collection-----------------------------------------------------
        report = collection.insert_one(exp)
        session['reportid'] = report.inserted_id
        return redirect(url_for("getit"))
    return render_template("constat_form/addreport"+nbr+".html",lang=lang)
#----------------wfet end-----------------------------------------------------------------------------------
if __name__ == "__main__":
    app.run()