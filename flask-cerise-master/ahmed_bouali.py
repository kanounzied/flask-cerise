from flask import Flask, render_template, request, redirect, url_for, session
from flask_pymongo import PyMongo
from flask_assets import Environment, Bundle
import uuid
import pdfkit
from flask import make_response
from datetime import datetime

app = Flask(__name__)
app.config['MONGO_URI'] = "mongodb://localhost:27017/VIE"
app.config['UPLOAD_FOLDER'] = '.'
mongo = PyMongo(app)

app.config.from_object(__name__)
assets = Environment(app)
assets.url = app.static_url_path
assets.debug = True
scss = Bundle('styles/stylesheet2.scss', filters='pyscss', output='gen/all.css')
assets.register('scss_all', scss)

app.secret_key = "secret_key"

d = dict(
    zip(['vie0', 'vie1', 'vie2', 'vie22', 'vie3', 'vie33', 'vie333', 'vie4', 'vie44', 'vie5', 'vie55', 'vie6'],
        [False for i in range(12)]))


@app.route("/", methods=['POST', 'GET'])
def home():
    try:
        session['lang'] = request.args.get('lang')
        if not (session['lang']):
            raise Exception()
    except:
        session['lang'] = 'fr'
    if request.method == 'POST':
        fn = request.form.get('first_name')
        ln = request.form.get('last_name')
        session['fn'] = fn
        session['ln'] = ln

        if fn and ln:
            session['vie0'] = True
            return redirect(url_for("vie1"))
    for key in d:
        session[key] = d[key]
    return render_template('vie/sign.html', lang=session['lang'])


@app.route('/vie/1', methods=['POST', 'GET'])
def vie1():
    error=''
    cursor = mongo.db['adress'].find({})
    print(cursor)
    data = []
    print(mongo.db['adress'].count_documents({}))
    for v in cursor:
        print(v)
        try:
            data.append(v['field1'] + ' ' + v['field2'][0:-2].replace(';', ' '))
        except:
            pass
    print(data)
    if request.method == 'POST':
        session['adress'] = request.form.get('adresse')
        session['code'] = session["adress"][-5:-1]
        if session['adress'] and session['code'].isnumeric():
            session['vie1'] = True
            return redirect(url_for("vie2"))
        else:
            error = {'fr': "L'adresse doit être non vide et le code numérique!",
                     'en': 'Enter a non void adress and a number for the code', 'ar': "أدخل عنوان و رمز رقمي"}
    if not (session['vie0']):
        return redirect(url_for("home"))
    return render_template('vie/vie1.html', lang=session['lang'], data=data, error=error)


@app.route('/vie/2', methods=['POST', 'GET'])
def vie2():
    erreur = ''
    if request.method == 'POST' and session['vie1']:
        session['age'] = request.form.get('age')
        if session['age'].isnumeric() and int(session['age'])>0:
            session['vie2'] = True
            return redirect(url_for("vie22"))
        else:
            erreur = {'fr':"L'age doit être une valeur numérique non vide",'en':"Enter a non void number",'ar':"أدخل رقما"}
    if not (session['vie1']):
        return redirect(url_for("vie1"))
    return render_template('vie/vie2.html', lang=session['lang'], error=erreur)


@app.route('/vie/22', methods=['POST', 'GET'])
def vie22():
    error=''
    if request.method == 'POST' and session['vie2']:
        session['sex'] = request.form.get('sex')
        if session['sex']:
            session['vie22'] = True
            return redirect(url_for("vie3"))
        else:
            error = {'fr':"",'en':"",'ar':""}
    if not (session['vie2']):
        return redirect(url_for("vie2"))
    return render_template('vie/vie22.html', lang=session['lang'])


@app.route('/vie/3', methods=['POST', 'GET'])
def vie3():
    error =""
    if request.method == 'POST' and session['vie22']:
        session['w'] = request.form.get('w')
        session['h'] = request.form.get('h')

        if session['w'].isnumeric() and 15 < int(session['w']) < 300 and session['h'].isnumeric() and 15 < int(session['h']) < 300:
            session['vie3'] = True
            session['bmi'] = float(session['w'])/(float(session['h'])/100)*(float(session['h'])/100)
            return redirect(url_for('vie33'))
        else:
            error = {'fr':"Taper votre taille et votre poids",'en':'Provide height and wieght','ar':'أدخل طولك و وزنك'}
    if not (session['vie22']):
        return redirect(url_for("vie22"))
    return render_template('vie/vie3.html', lang=session['lang'], error=error)


@app.route('/vie/33', methods=['POST', 'GET'])
def vie33():
    if request.method == 'POST' and session['vie3']:
        session['smoke'] = request.form.get('smoke')
        if session['smoke']:
            session['vie33'] = True
            return redirect(url_for('vie333'))
    if not (session['vie3']):
        return redirect(url_for("vie3"))
    return render_template('vie/vie33.html', lang=session['lang'])


@app.route('/vie/333', methods=['POST', 'GET'])
def vie333():
    if request.method == 'POST' and session['vie33']:
        session['drink'] = request.form.get('drink')
        if session['drink']:
            session['vie333'] = True
            return redirect(url_for('vie4'))
    if not (session['vie33']):
        return redirect(url_for("vie33"))
    return render_template('vie/vie333.html', lang=session['lang'])


@app.route('/vie/4', methods=['POST', 'GET'])
def vie4():
    error=''
    if request.method == 'POST' and session['vie333']:
        session['status'] = request.form.get('status')
        if session['status']:
            session['vie4'] = True
            return redirect(url_for('vie44'))
        else:
            error={'fr':'Selectionnez une option', 'en':'Select an option', 'ar':'إختر من القائمة'}
    if not (session['vie333']):
        return redirect(url_for("vie333"))
    return render_template('vie/vie4.html', lang=session['lang'], error=error)


@app.route('/vie/44', methods=['POST', 'GET'])
def vie44():
    error=''
    if request.method == 'POST' and session['vie4']:
        session['children'] = request.form.get('children')
        if session['children'].isnumeric() and int(session['children'])<=10:
            session['vie44'] = True
            return redirect(url_for('vie5'))
        else:
            error = {"fr":"Taper un entier positif ou nul inférieur à 10" ,"en":"Type a positif or null integer less than 10","ar":"أدخل رقما موجب أصغر من 10" }
    if not (session['vie4']):
        return redirect(url_for("vie4"))
    return render_template('vie/vie44.html', lang=session['lang'], error=error)


@app.route('/vie/5', methods=['POST', 'GET'])
def vie5():
    error = ''
    if request.method == 'POST' and session['vie44']:
        session['salary'] = request.form.get('salary')
        if session['salary'].isnumeric():
            session['vie5'] = True
            return redirect(url_for('vie55'))
        else:
            error = {"fr":"Taper un entier positif ou nul" ,"en":"Type a positif or null integer","ar":"أدخل رقما أكبر أو يساوي صفر" }

    if not (session['vie44']):
        return redirect(url_for("vie44"))
    return render_template('vie/vie5.html', lang=session['lang'], error=error)


@app.route('/vie/55', methods=['POST', 'GET'])
def vie55():
    error=''
    if request.method == 'POST' and session['vie5']:
        session['debt'] = request.form.get('debt')
        if session['debt'].isnumeric():
            session['vie55'] = True
            return redirect(url_for('vie6'))
        else:
            error = {"fr":"Taper un entier positif ou nul" ,"en":"Type a positif or null integer","ar":"أدخل رقما أكبر أو يساوي صفر" }

    if not (session['vie5']):
        return redirect(url_for("vie5"))
    return render_template('vie/vie55.html', lang=session['lang'],error=error)


@app.route('/vie/6', methods=['POST', 'GET'])
def vie6():
    if request.method == 'POST' and session['vie55']:
        f = request.files['file']
        string = str(uuid.uuid4())
        f.save("{}.pdf".format(string))
        print(string)
        if f:
            session['vie6'] = True
            print('aaaaaaaaaaaaaaaaaaaaaa')
            mongo.db.clients.insert(
                {'first_name': session['fn'], 'last_name': session['ln'], 'adresse': session['adress'],
                 'code': session['code'], 'sex': session['sex'], 'age': session['age'],
                 'bmi': session['bmi']
                    , 'smoke': session['smoke'], 'drink': session['drink'],
                 'status': session['status'], 'children': session['children'],
                 'salary': session['salary'], 'debt': session['debt'], 'file': string})
            print(session['adress'])
            return redirect(url_for('generate'))
    if not (session['vie55']):
        return redirect(url_for("vie55"))
    return render_template('vie/vie6.html', lang=session['lang'])


@app.route("/result/", methods=['POST', 'GET'])
def result():
    """

    :param data:
    :return:

    Here I need to calculate the result based on the dict object
    """
    return '<h1>Building Page Result ...</h1>'
    #return render_template("preview.html", lang=session['lang'])

def formule(x,y,z):
    return (x - 0.01*y)*(1+0.01*(100-z))

@app.route('/gen/contract')
def generate():
    info = [['BMI',session['bmi']]
                    , ['Fumeur', session['smoke']], ['Alcool', session['drink']],
                 ['Statut familial', session['status']], ["Nombre d'enfants",session['children']]]
    css=['./templates/contrat/contrat.css', './templates/contrat/bootstrap.min.css']
    print(session['adress'])
    print(session['sex'])
    rendered = render_template('contrat/contrat.html',
                               fn=session['fn'],
                               ln=session['ln'],
                               adress=session['adress'],
                               sex=session['sex'],
                               age=session['age'],
                               somme=formule(int(session['salary']),int(session['debt']),int(session['age'])),
                               dateb = datetime.now().date(),
                               contrat=0,
                               info=info)
    pdf = pdfkit.from_string(rendered, False,css=css)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = "inline; filename=output.pdf"
    return response







# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
