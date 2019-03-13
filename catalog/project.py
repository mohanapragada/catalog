from flask import Flask, render_template, url_for
from flask import request, redirect, flash, make_response, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Data_Setup import Base, CarCompanyName, CarName, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
import datetime

engine = create_engine('sqlite:///cars.db',
                       connect_args={'check_same_thread': False}, echo=True)
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json',
                            'r').read())['web']['client_id']
APPLICATION_NAME = "Cars Store"

DBSession = sessionmaker(bind=engine)
session = DBSession()
tb_car = session.query(CarCompanyName).all()


@app.route('/login')
def showLogin():
    ''' Login to application '''

    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    tb_car = session.query(CarCompanyName).all()
    crs = session.query(CarName).all()
    return render_template('login.html',
                           STATE=state, tb_car=tb_car, crs=crs)


@app.route('/gconnect', methods=['POST'])
def gconnect():

    ''' Validate state token '''

    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    ''' Obtain authorization code '''
    code = request.data

    try:
        ''' Upgrade the authorization code into a credentials object '''
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    ''' Check that the access token is valid. '''
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    ''' If there was an error in the access token info, abort. '''
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    ''' Verify that the access token is used for the intended user.'''
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    '''Verify that the access token is valid for this app.'''
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print ("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    ''' Store the access token in the session for later use.'''
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    ''' see if user exists, if it doesn't make a new one '''
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px; border-radius: 150px;'
    '-webkit-border-radius: 150px; -moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print ("done!")
    return output


def createUser(login_session):
    ''' User Helper Functions '''
    U1 = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(U1)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception as error:
        print(error)
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/')
@app.route('/home')
def home():
    ''' Display the Home page '''
    tb_car = session.query(CarCompanyName).all()
    return render_template('myhome.html', tb_car=tb_car)

#####
# Car Category for admins


@app.route('/CarStore')
def CarStore():
    '''Diaplayed by the Main Page of CarGarage '''
    try:
        if login_session['username']:
            name = login_session['username']
            tb_car = session.query(CarCompanyName).all()
            tb = session.query(CarCompanyName).all()
            crs = session.query(CarName).all()
            return render_template('myhome.html', tb_car=tb_car,
                                   tb=tb, crs=crs, uname=name)
    except:
        return redirect(url_for('showLogin'))


@app.route('/CarStore/<int:crid>/AllCompanys')
def showCars(crid):
    ''' Showing cars based on car category '''
    tb_car = session.query(CarCompanyName).all()
    tb = session.query(CarCompanyName).filter_by(id=crid).one()
    crs = session.query(CarName).filter_by(carcompanynameid=crid).all()
    try:
        if login_session['username']:
            return render_template('showCars.html', tb_car=tb_car,
                                   tb=tb, crs=crs,
                                   uname=login_session['username'])
    except:
        return render_template('showCars.html',
                               tb_car=tb_car, tb=tb, crs=crs)


@app.route('/CarStore/addCarCompany', methods=['POST', 'GET'])
def addCarCompany():
    ''' Add New CarCompany '''
    if 'username' not in login_session:
        flash("Please log in to continue.")
        return redirect(url_for('showLogin'))
    if request.method == 'POST':
        company = CarCompanyName(name=request.form['name'],
                                 user_id=login_session['user_id'])
        session.add(company)
        session.commit()
        return redirect(url_for('CarStore'))
    else:
        return render_template('addCarCompany.html', tb_car=tb_car)


@app.route('/CarStore/<int:crid>/edit', methods=['POST', 'GET'])
def editCarCategory(crid):
    ''' Edit Car Category '''
    editCar = session.query(CarCompanyName).filter_by(id=crid).one()
    creator = getUserInfo(editCar.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot edit this Car Category."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('CarStore'))
    if request.method == "POST":
        if request.form['name']:
            editCar.name = request.form['name']
        session.add(editCar)
        session.commit()
        flash("Car Category Edited Successfully")
        return redirect(url_for('CarStore'))
    else:
        return render_template('editCarCategory.html',
                               cr=editCar, tb_car=tb_car)


@app.route('/CarStore/<int:crid>/delete', methods=['POST', 'GET'])
def deleteCarCategory(crid):
    ''' Delete Car Category '''
    cr = session.query(CarCompanyName).filter_by(id=crid).one()
    creator = getUserInfo(cr.user_id)
    user = getUserInfo(login_session['user_id'])
    if creator.id != login_session['user_id']:
        flash("You cannot Delete this Car Category."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('CarStore'))
    if request.method == "POST":
        session.delete(cr)
        session.commit()
        flash("Car Category Deleted Successfully")
        return redirect(url_for('CarStore'))
    else:
        return render_template('deleteCarCategory.html', cr=cr, tb_car=tb_car)


@app.route('/CarStore/addCompany/addCarDetails/<string:crname>/add',
           methods=['GET', 'POST'])
def addCarDetails(crname):
    '''
     Add New Car Name Details '''
    tb = session.query(CarCompanyName).filter_by(name=crname).one()
    ''' See if the logged in user is not the owner of car '''
    creator = getUserInfo(tb.user_id)
    user = getUserInfo(login_session['user_id'])
    if creator.id != login_session['user_id']:
        flash("You can't add new book edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showCars', crid=tb.id))
    if request.method == 'POST':
        name = request.form['name']
        color = request.form['color']
        cc = request.form['cc']
        price = request.form['price']
        cartype = request.form['cartype']
        cardetails = CarName(name=name,
                             color=color, cc=cc,
                             price=price,
                             cartype=cartype,
                             date=datetime.datetime.now(),
                             carcompanynameid=tb.id,
                             user_id=login_session['user_id'])
        session.add(cardetails)
        session.commit()
        return redirect(url_for('showCars', crid=tb.id))
    else:
        return render_template('addCarDetails.html',
                               crname=tb.name, tb_car=tb_car)


@app.route('/CarStore/<int:crid>/<string:crsname>/edit',
           methods=['GET', 'POST'])
def editCar(crid, crsname):
    ''' Edit Car details '''
    cr = session.query(CarCompanyName).filter_by(id=crid).one()
    cardetails = session.query(CarName).filter_by(name=crsname).one()
    ''' See if the logged in user is not the owner of car '''
    creator = getUserInfo(cr.user_id)
    user = getUserInfo(login_session['user_id'])
    if creator.id != login_session['user_id']:
        flash("You can't edit this book edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showCars', crid=cr.id))
    ''' POST methods '''
    if request.method == 'POST':
        cardetails.name = request.form['name']
        cardetails.color = request.form['color']
        cardetails.cc = request.form['cc']
        cardetails.price = request.form['price']
        cardetails.cartype = request.form['cartype']
        cardetails.date = datetime.datetime.now()
        session.add(cardetails)
        session.commit()
        flash("Car Edited Successfully")
        return redirect(url_for('showCars', crid=crid))
    else:
        return render_template('editCar.html',
                               crid=crid, cardetails=cardetails, tb_car=tb_car)


@app.route('/CarStore/<int:crid>/<string:crsname>/delete',
           methods=['GET', 'POST'])
def deleteCar(crid, crsname):
    ''' Delte Car Edit '''
    cr = session.query(CarCompanyName).filter_by(id=crid).one()
    cardetails = session.query(CarName).filter_by(name=crsname).one()
    ''' See if the logged in user is not the owner of car '''
    creator = getUserInfo(cr.user_id)
    user = getUserInfo(login_session['user_id'])
    if creator.id != login_session['user_id']:
        flash("You can't delete this book edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showCars', crid=cr.id))
    if request.method == "POST":
        session.delete(cardetails)
        session.commit()
        flash("Deleted Car Successfully")
        return redirect(url_for('showCars', crid=cr.id))
    else:
        return render_template('deleteCar.html',
                               crid=crid, cardetails=cardetails, tb_car=tb_car)


@app.route('/logout')
def logout():
    ''' Logout from current user '''
    access_token = login_session['access_token']
    print ('In gdisconnect access token is %s', access_token)
    print ('User name is: ')
    print (login_session['username'])
    if access_token is None:
        print ('Access Token is None')
        response = make_response(
            json.dumps('Current user not connected....'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = login_session['access_token']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = \
        h.request(uri=url, method='POST', body=None,
                  headers={'content-type':
                           'application/x-www-form-urlencoded'})[0]

    print (result['status'])
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps
                                 ('Successfully disconnected user..'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("Successful logged out")
        return redirect(url_for('showLogin'))
        # return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response
'''Json Files'''


@app.route('/CarStore/JSON')
def allCarsJSON():
    carcategories = session.query(CarCompanyName).all()
    category_dict = [c.serialize for c in carcategories]
    for c in range(len(category_dict)):
        cars = [i.serialize for i in session.query(CarName).
                filter_by(carcompanynameid=category_dict[c]["id"]).all()]
        if cars:
            category_dict[c]["car"] = cars
    return jsonify(CarCompanyName=category_dict)


@app.route('/carStore/carCategories/JSON')
def categoriesJSON():
    cars = session.query(CarCompanyName).all()
    return jsonify(carCategories=[c.serialize for c in cars])


@app.route('/carStore/cars/JSON')
def itemsJSON():
    items = session.query(CarName).all()
    return jsonify(cars=[i.serialize for i in items])


@app.route('/carStore/<path:car_name>/cars/JSON')
def categoryItemsJSON(car_name):
    carCategory = session.query(CarCompanyName).filter_by(name=car_name).one()
    cars = session.query(CarName).filter_by(carcompanyname=carCategory).all()
    return jsonify(carEdtion=[i.serialize for i in cars])


@app.route('/carStore/<path:car_name>/<path:edition_name>/JSON')
def ItemJSON(car_name, edition_name):
    carCategory = session.query(CarCompanyName).filter_by(name=car_name).one()
    carEdition = session.query(CarName).filter_by(
           name=edition_name, carcompanyname=carCategory).one()
    return jsonify(carEdition=[carEdition.serialize])

if __name__ == '__main__':
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='127.0.0.1', port=8000)
