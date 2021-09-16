import os, json, string, random
from flask.wrappers import Response
import requests
from datetime import datetime
from flask import render_template, request,flash,redirect,url_for,session

from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
from werkzeug.wrappers import response

from bapp import app,db
from bapp.model import Favourites, Member, Technology, Contact, States, Local_governments, Transaction
from bapp.form import LoginForm


@app.route('/test')
def test():
    loggedin = session.get('userid')
    data = Member.query.get(loggedin)
    return render_template('user/report.html', data=data)


@app.route('/')
def home():
    loggedin = session.get('userid')
    thisweek = datetime.today() #as an obj
    weekno = thisweek.strftime('%U')
    allusers = db.session.query(Member).all()
    #create a new list of those whose birthday falls in the current week
    celebrants = []
    for i in allusers:
        dob_weekno = (i.member_dob).strftime('%U')
        if dob_weekno == weekno:
            celebrants.append(i)
    if loggedin != None:
        data = Member.query.filter(Member.member_id == loggedin).first()
        return render_template('user/index.html',data=data,allusers=allusers,weekno=weekno,celebrants=celebrants)
    else:
        return render_template('user/index.html')

@app.route('/newfav', methods=['POST'])
def newfav():
    loggedin = session.get('userid')
    myfav = request.form.getlist('techid') #[2,4,8]
    
    allfavs = Favourites.query.filter(Favourites.fav_memberid==loggedin).all()  #[<Favourites 1>, <favourites2>]
    #delete all instances of Favourites belonging to this user
    for t in allfavs:  
        db.session.delete(t)
        db.session.commit()
    #fresh insertion

    for i in myfav:
        f = Favourites(fav_techid=i,fav_memberid=loggedin)
        db.session.add(f)
    db.session.commit()
    return redirect(url_for('fav'))
   

@app.route('/uploadimage', methods=['POST','GET'])
def uploadimage():
    loggedin = session.get('userid')
    if loggedin !=None:
        data = Member.query.get(loggedin)
        if request.method =='GET':
            return render_template('user/photo.html',data=data)
        else:
            #retrieve file
            pic = request.files.get('pix') #name on the form
            filename = pic.filename
            #carry out checks before you save
            pic.save(f'bapp/static/profile/{filename}')
            #update the db for this user
            userobj = Member.query.get(loggedin)
            userobj.member_pix=filename
            db.session.commit()

            return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('home'))


@app.route('/fav')
def fav():
    loggedin = session.get('userid')
    if loggedin != None:
        data = Member.query.filter(Member.id==loggedin).first()

        myfavs = Favourites.query.filter(Favourites.fav_memberid== loggedin).all()  #[<Favourites 1>, <favourites2>]

        myfav_techid = [] 
        for x in myfavs:
            myfav_techid.append(x.fav_techid)     #[1,3,6]  

        # similar result as above
        # myfavs = db.session.query(Favourites,Technology).join(Technology).filter_by(fav_memberid=loggedin).all()

        techs = db.session.query(Technology).all()        
      

        return render_template('user/fav.html', data=data,myfavs=myfavs,techs=techs, myfav_techid=myfav_techid)
    else:
        return redirect(url_for('home'))

@app.route('/editprofile', methods=['POST','GET'])
def editprofile():
    loggedin = session.get('userid')
    if request.method =='GET':        
        if loggedin !=None:
            data = Member.query.filter(Member.id == loggedin).first()
            return render_template('user/profile.html', data=data)
        else:
            return redirect(url_for('home'))
    else:
        #pick items from the form
        fname = request.form['fname']
        lname = request.form['lname']
        dob = request.form['dob'] #dd/mm/yyyy

        #datetime.strptime(date_string, format) to convert from string to datetime
        dob_datetime = datetime.strptime(dob,'%d/%m/%Y')
        #yyyy-mm-dd
        formated_date = dob_datetime.strftime('%Y-%m-%d')

        #you can validate here before you update the record in the db
        m = Member.query.get(loggedin) #object of the logged in user
        m.member_fname = f"{fname}"
        m.member_lname = f"{lname}"
        m.member_dob = f"{formated_date}"

        db.session.commit()
        flash(f'Your data has been updated! {dob} and {formated_date}')
        return redirect(url_for('editprofile'))
        


@app.route('/registration', methods=['POST','GET'])
def registration():
    if request.method=='GET':
        return render_template('user/register.html')
    else:
        #retrieve form data
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        email = request.form.get('email')
        password = request.form.get('pass1')
        password2 = request.form.get('pass2')
        
        if password != password2:
            flash('The two passwords must match!')
            return redirect('/registration')
        else:
            #insert into database
            enc_pass = generate_password_hash(password)
            m = Member(member_fname=fname,member_lname=lname,member_email=email,member_phone='',member_pwd=enc_pass,member_pix='')
            db.session.add(m)
            db.session.commit()
            session['userid'] = m.id
            flash('Congrats! you are now a member of Cohort 18 Python Class')
            return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    loggedin = session.get('userid')
    if loggedin != None:
        data = Member.query.filter(Member.id==loggedin).first()
        picture=''
        if data.member_pix !='':
            picture = os.path.join('static/profile/',data.member_pix)
            # picture = f'static/profile/{data.member_pix}'

        return render_template('user/dashboard.html',data=data,picture=picture)
    else:
        return redirect(url_for('home'))

@app.route('/logout')
def logout():
    if session.get('userid') !=None:
        session.pop('userid')
    return redirect(url_for('home'))
    

@app.route('/login',methods=['POST','GET'])
def loginpage():
    logform = LoginForm()
    if request.method=='GET':
        return render_template('user/login.html',logform=logform)
    else:
        #retrieve data from form
        if logform.validate_on_submit():
            username = request.form.get('username') 
            password = logform.password.data 
            deets = Member.query.filter(Member.member_email==username).first()
            if deets != None:
                stored_hash = deets.member_pwd
                check = check_password_hash(stored_hash,password)

                if check:                  
                    session['userid'] = deets.id 

                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid Details, try again')
                    return redirect(url_for('loginpage'))
            else:
                flash('Invalid Details, try again')
                return redirect(url_for('loginpage')) 

        else:
            return render_template('user/login.html',logform=logform)


@app.route('/contact')
def contact():

    return render_template('user/contactpage.html')

@app.route('/submit', methods=['POST'])
def submit():

    user = request.form.get('fname')

    mess = request.form.get('message') 
    
    b = Contact(contact_name=user, contact_message=mess)

    y = request.form.get('feed')
    db.session.add(b)
    db.session.commit()
    
    # return render_template('user/contactpage.html')
    return f'Form submitted, Thank you. Name: {user}, Message: {mess} {y}'

@app.route('/available')
def available():

    fullname = request.args.get('fullname')

    data = Contact.query.filter(Contact.contact_name==fullname).first()

    if data:
        sendback = {'message':'Name has been taken', 'status': 0}
        return json.dumps(sendback)


    else:
        sendback = {'message':'Name Available', 'status': 1}
        return json.dumps(sendback)

    
@app.route('/allstate')
def state():
    deets = States.query.all()
    return render_template('user/state.html', deets=deets )

@app.route('/xchn')
def xchn():
    stateid = request.form.get('stateid')
    lgas = Local_governments.query.filter(Local_governments.state_id==stateid).all()

    lga_dropdown = "<select name=''  class='form-control'> "
    for i in lgas:
        lga_dropdown = lga_dropdown + f"<option value='{i.id}'>"+i.name+"</option>"
    lga_dropdown = lga_dropdown + "</select>"

    return lga_dropdown

def generate_ref():
    content = random.sample(string.digits,10)
    r = ''.join(content)
    return r

@app.route('/donate', methods=['POST','GET'])
def donate():
    loggedin = session.get('userid')
    if loggedin != None:
        data = Member.query.get(loggedin)
        if request.method =='GET':
            return render_template('user/donation.html',data=data)
        else:
            amt = request.form.get('amt')
            refno = generate_ref()
            session['ref'] = refno
            amtkobo=float(amt)*100
            t = Transaction(trx_status='Pending',trx_ref=refno,trx_memberid=loggedin,trx_amt=amtkobo)

            db.session.add(t)
            db.session.commit()
            return redirect(url_for('confirmation'))

@app.route('/donate2')
def donate2():
    loggedin = session.get('userid')
    if loggedin != None:
        ref = session['ref']

        #data = Member.query.filter(Member.id==loggedin).first()
        t = Transaction.query.filter(Transaction.trx_ref==ref).first()
        amt = t.trx_amt

        user_email = t.user.member_email

        headers = {"Content-Type": "application/json", "Authoriztion":"Bearer sk_test_78c3d2ffa302ff030542ece4318b6955fa30522b", "Cache-Control":"no-cache"}

        data = {"reference": ref, "amount": amt, "email": user_email}

        newdata = json.dumps(data)
        
        response=requests.post('https://api.paystack.co/transaction/initialize', headers=headers, data=newdata)

        response_json = response.json()
        if response_json['status'] == True:
            auth_url = response_json['data']['authorization_url']
            return redirect(auth_url)
        else:
            flash('Please Try again')
            return redirect(url_for('donate'))
    else:
        return redirect(url_for('home'))

@app.route('/confirmation')
def confirmation():
    loggedin = session.get('userid')
    refno = session.get('ref')
    if loggedin != None:
        deets = db.session.query(Transaction).filter(Transaction.trx_ref==refno).first()
        return render_template('user/confirmation.html', deets=deets)
        
    
    else:
        return redirect('/')

@app.route('/payverify')
def payverify():
    loggedin = session.get('userid')
    refno = session.get('ref')
    trxref = request.args.get('trxref')

    headers = {"Content-Type": "application/json", "Authoriztion":"Bearer pk_test_da64e742b19e0f052b9692792c003eae34eb0061", "Cache-Control":"no-cache"}

    response = requests.get(f'https://api.paystack.co/transaction/verify/:{trxref}', headers=headers)

    rsp = response.json()

    return rsp

@app.route('/hostels')
def hostel():
    response = requests.get('http://127.0.0.1:5000/api/v1.0/list')

    # response = requests.post('http://127.0.0.1:5000/hostel/api/v1.o/create', headers=headers, data=data)

    rsp = response.json()
    # rsp = json.loads(response.text)
    return render_template('user/hostels.html', rsp=rsp)



@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response