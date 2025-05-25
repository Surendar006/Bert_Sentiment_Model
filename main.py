# main.py
import os
import base64
import io
import math
from flask import Flask, render_template, Response, redirect, request, session, abort, url_for
import mysql.connector
import hashlib
import datetime
import calendar
import random
from random import randint
from urllib.request import urlopen
import webbrowser
from plotly import graph_objects as go
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import plotly.express as px
from werkzeug.utils import secure_filename
from PIL import Image
import urllib.request
import urllib.parse
import socket    
import csv

import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

nltk.download('punkt')
nltk.download('stopwords')

import matplotlib as mpl
import seaborn as sns
from matplotlib import pyplot as plt
from collections import OrderedDict
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from wordcloud import WordCloud
from textblob import TextBlob
#import torch
#import torch.nn.functional as F
#from torch_geometric.nn import GATConv

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  charset="utf8",
  database="review_aspect"

)
app = Flask(__name__)
##session key
app.secret_key = 'abcdef'
#######
UPLOAD_FOLDER = 'static/upload'
ALLOWED_EXTENSIONS = { 'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#####
@app.route('/', methods=['GET', 'POST'])
def index():
    msg=""

    
    if request.method=='POST':
        uname=request.form['uname']
        pwd=request.form['pass']
        cursor = mydb.cursor()
        cursor.execute('SELECT * FROM cs_register WHERE uname = %s AND pass = %s', (uname, pwd))
        account = cursor.fetchone()
        if account:

            
            session['username'] = uname
            return redirect(url_for('userhome'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('index.html',msg=msg)

@app.route('/alert_mail', methods=['GET', 'POST'])
def alert_mail():
    msg=""
    mdata=[]
    st=""
    mycursor = mydb.cursor()
    mycursor.execute('SELECT * FROM admin')
    rw = mycursor.fetchone()
    ah=rw[3]
    am=rw[4]
    status=rw[5]
    cdate=rw[6]
    
    mycursor.execute('SELECT * FROM cs_register WHERE offer_type=0')
    dd = mycursor.fetchall()

    import datetime
    now1 = datetime.datetime.now()
    rdate=now1.strftime("%d-%m-%Y")
    edate1=now1.strftime("%Y-%m-%d")
    rtime=now1.strftime("%H:%M")
    #print(rtime)
    
    rtime1=rtime.split(':')
    rh=int(rtime1[0])
    rm=int(rtime1[1])


    if ah==rh and rm>=am:
        if rdate==cdate:
            if status<2:
                st="1"
                mycursor.execute("update admin set status=status+1,rdate=%s",(rdate,))
                mydb.commit()
                for ds in dd:
                    md=[]
                    name=ds[1]
                    email=ds[3]
                    print(email)

                    subj=""
                    mess=""
                    mycursor.execute('SELECT * FROM cs_email order by rand() limit 0,1')
                    gg = mycursor.fetchall()
                    for g1 in gg:
                        
                        subj=g1[1]
                        mess=g1[2]

                    mess1="Dear "+name+", "+mess
                    md.append(email)
                    md.append(subj)
                    md.append(mess1)
                    mdata.append(md)
                    #print(mdata)
        else:
            mycursor.execute("update admin set rdate=%s",(rdate,))
            mydb.commit()
        
            

    
    
    
    
        
    return render_template('alert_mail.html',msg=msg,mdata=mdata,st=st)


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg=""

    
    if request.method=='POST':
        uname=request.form['uname']
        pwd=request.form['pass']
        cursor = mydb.cursor()
        cursor.execute('SELECT * FROM admin WHERE username = %s AND password = %s', (uname, pwd))
        account = cursor.fetchone()
        if account:
            session['username'] = uname
            return redirect(url_for('admin'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('login.html',msg=msg)

@app.route('/register', methods=['GET', 'POST'])
def register():
    #import student
    msg=""
    cusid=""
    off_type=""
    rdate=""
    loc=""
    #filename = 'static/dataset/dataset_review.csv'
    #data1 = pd.read_csv(filename, header=0)

    mycursor = mydb.cursor()
    mycursor.execute("SELECT max(id)+1 FROM cs_register")
    maxid = mycursor.fetchone()[0]
    if maxid is None:
        maxid=1

    j=1
    '''for ds in data1.values:
        if j==maxid:
            cusid=ds[0]
            segment=ds[9]
            rdate=ds[4]
            loc=ds[3]
            if segment=="Gold Customer":
                off_type="2"
            elif segment=="Silver Customer":
                off_type="1"
            else:
                off_type="0"
            break
        j+=1'''    

    #import datetime
    #now1 = datetime.datetime.now()
    #rdate=now1.strftime("%d-%m-%Y")
    
    if request.method=='POST':
        name=request.form['name']
        mobile=request.form['mobile']
        email=request.form['email']
        uname=request.form['uname']
        pass1=request.form['password']
        gender=request.form['gender']
        age=request.form['age']
        location=request.form['location']
    
        
        
        mycursor.execute("SELECT count(*) FROM cs_register where uname=%s",(uname,))
        cnt = mycursor.fetchone()[0]

        if cnt==0:
            
                    
            sql = "INSERT INTO cs_register(id,name,mobile,email,uname,pass,gender,offer_type,customer_id,age,location,rdate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = (maxid,name,mobile,email,uname,pass1,gender,off_type,cusid,age,location,rdate)
            mycursor.execute(sql, val)
            mydb.commit()            
            #print(mycursor.rowcount, "Registered Success")
            msg="sucess"
            #if mycursor.rowcount==1:
            return redirect(url_for('index'))
        else:
            msg='Already Exist'
    return render_template('register.html',msg=msg,cusid=cusid,loc=loc)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    msg=""
    act = request.args.get('act')
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM cs_category")
    data = mycursor.fetchall()

    
        
    if request.method=='POST':
        category=request.form['category']
        product=request.form['product']
        price=request.form['price']
        detail=request.form['detail']
        
    
        file = request.files['file']
        mycursor.execute("SELECT max(id)+1 FROM cs_product")
        maxid = mycursor.fetchone()[0]
        if maxid is None:
            maxid=1
            
        try:
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file:
                fn=file.filename
                fnn="P"+str(maxid)+fn  
                #fn1 = secure_filename(fn)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], fnn))
                
        except:
            print("dd")
        
        

        photo="P"+str(maxid)+fn   
        sql = "INSERT INTO cs_product(id,category,product,price,photo,detail) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (maxid,category,product,price,photo,detail)
        mycursor.execute(sql, val)
        mydb.commit()            
        #print(mycursor.rowcount, "Registered Success")
        result="sucess"
        if mycursor.rowcount==1:
            return redirect(url_for('add_product'))
        else:
            msg='Already Exist'

    if act=="del":
        did = request.args.get('did')
        mycursor.execute('delete from cs_product WHERE id = %s', (did, ))
        mydb.commit()
        return redirect(url_for('add_product'))

    
        
    mycursor.execute("SELECT * FROM cs_product")
    data2 = mycursor.fetchall()
    
    return render_template('add_product.html',msg=msg,data=data,data2=data2)

@app.route('/offer', methods=['GET', 'POST'])
def offer():
    msg=""
    act = request.args.get('act')
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM cs_offer")
    data = mycursor.fetchall()


    
    return render_template('offer.html',msg=msg,data=data)

@app.route('/offer_edit', methods=['GET', 'POST'])
def offer_edit():
    msg=""
    fid = request.args.get('fid')
    act = request.args.get('act')
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM cs_offer where id=%s",(fid,))
    data = mycursor.fetchone()

    
        
    if request.method=='POST':
        offer=request.form['offer']
        min_purchase=request.form['min_purchase']
        discount=request.form['discount']
        mycursor.execute("update cs_offer set offer=%s,min_purchase=%s,discount=%s where id=%s",(offer,min_purchase,discount,fid))
        mydb.commit()
        
        return redirect(url_for('offer'))
        
      
    return render_template('offer_edit.html',msg=msg,data=data)

@app.route('/view_cus', methods=['GET', 'POST'])
def view_cus():
    msg=""
    act = request.args.get('act')
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM cs_register where offer_type=0")
    data = mycursor.fetchall()


    
    return render_template('view_cus.html',msg=msg,data=data)

@app.route('/cus_edit', methods=['GET', 'POST'])
def cus_edit():
    msg=""
    cid = request.args.get('cid')
    act = request.args.get('act')
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM cs_register where id=%s",(cid,))
    data = mycursor.fetchone()

    
        
    if request.method=='POST':
        email=request.form['email']
       
        mycursor.execute("update cs_register set email=%s where id=%s",(email,cid))
        mydb.commit()
        
        return redirect(url_for('view_cus'))
        
      
    return render_template('cus_edit.html',msg=msg,data=data)



@app.route('/cus_alert', methods=['GET', 'POST'])
def cus_alert():
    msg=""
    
    act = request.args.get('act')
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM admin")
    data = mycursor.fetchone()

    
        
    if request.method=='POST':
        a_hour=request.form['a_hour']
        a_minute=request.form['a_minute']
       
        mycursor.execute("update admin set a_hour=%s,a_minute=%s,status=0",(a_hour,a_minute))
        mydb.commit()
        
        return redirect(url_for('view_cus'))        
      
    return render_template('cus_alert.html',msg=msg,data=data)

@app.route('/cus_mail', methods=['GET', 'POST'])
def cus_mail():
    msg=""
    
    act = request.args.get('act')
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM cs_email")
    data = mycursor.fetchall()

    return render_template('cus_mail.html',msg=msg,data=data)

@app.route('/cus_edit2', methods=['GET', 'POST'])
def cus_edit2():
    msg=""
    cid = request.args.get('cid')
    act = request.args.get('act')
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM cs_email where id=%s",(cid,))
    data = mycursor.fetchone()

    
        
    if request.method=='POST':
        subject=request.form['subject']
        message=request.form['message']
       
        mycursor.execute("update cs_email set subject=%s,message=%s where id=%s",(subject,message,cid))
        mydb.commit()
        
        return redirect(url_for('cus_mail'))        
      
    return render_template('cus_edit2.html',msg=msg,data=data)

@app.route('/sale_edit', methods=['GET', 'POST'])
def sale_edit():
    msg=""
    fid = request.args.get('fid')
    act = request.args.get('act')
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM admin where username='admin'")
    data = mycursor.fetchone()

    
        
    if request.method=='POST':
        
        min_sale_count=request.form['min_sale_count']
        
        mycursor.execute("update admin set min_sale_count=%s where username='admin'",(min_sale_count,))
        mydb.commit()
        
        return redirect(url_for('offer'))
        
      
    return render_template('sale_edit.html',msg=msg,data=data)


@app.route('/userhome', methods=['GET', 'POST'])
def userhome():
    msg=""
    msg2=""
    cnt=0
    uname=""
    mess=""
    off_mess=""
    act = request.args.get('act')
    cat = request.args.get('cat')
    poffer = request.args.get('poffer')
    if 'username' in session:
        uname = session['username']
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM cs_register where uname=%s",(uname,))
    usr = mycursor.fetchone()
    name=usr[1]
    email=usr[3]
    uff=usr[7]


    mycursor.execute("SELECT * FROM cs_offer where offer_type=%s",(uff,))
    fd1 = mycursor.fetchone()
    offer=fd1[1]
    per=fd1[4]

    mycursor.execute("SELECT * FROM cs_message where off_type=%s order by rand()",(uff,))
    fd1 = mycursor.fetchall()
    for fd in fd1:
        off_mess=fd[1]
        
    mycursor.execute("SELECT * FROM cs_category")
    data2 = mycursor.fetchall()

    ########offer###############
    pur_amt=0
    oftype=0
    st=""
    mycursor.execute("SELECT count(*) FROM cs_cart where uname=%s && status=1",(uname,))
    fd1 = mycursor.fetchone()[0]
    print("ss")
    print(fd1)
    if fd1>0:
        mycursor.execute("SELECT sum(price) FROM cs_cart where uname=%s && status=1",(uname,))
        fd2 = mycursor.fetchone()[0]
        pur_amt=fd2
        print(pur_amt)

        mycursor.execute("SELECT count(*) FROM cs_offer where min_purchase<=%s && offer_type=2",(pur_amt,))
        fd3 = mycursor.fetchone()[0]

        mycursor.execute("SELECT count(*) FROM cs_offer where min_purchase<=%s && offer_type=1",(pur_amt,))
        fd4 = mycursor.fetchone()[0]

        if fd3>0:
            oftype=2
            print(oftype)
        elif fd4>0:
            oftype=1
            print(oftype)
        else:
            oftype=0

    if oftype==uff:
        st="1"
        print("st1")
    else:
        st="2"
        print("st2")

    print(usr[7])
    
    if oftype>0 and st=="2":
        mycursor.execute("SELECT * FROM cs_offer where offer_type=%s",(oftype,))
        data3 = mycursor.fetchone()
        offer=data3[1]
        print(offer)
        
        print("offer")
        
        msg2="yes"
        mess="Dear "+name+", "+offer+" offer for you, Recommended Products - Click http://localhost:5000/recommend1?user="+uname
        mycursor.execute("update cs_register set offer_type=%s where uname=%s",(oftype,uname))
        mydb.commit()
    ####################

    cc=""
    if cat is None:
        cc=""
    else:
        cc="1"
    
    if request.method=='POST':
        getval=request.form['getval']
        cat="%"+getval+"%"
        prd="%"+getval+"%"
        det="%"+getval+"%"
        mycursor.execute("SELECT * FROM cs_product where category like %s || product like %s || detail like %s  order by star desc",(cat,prd,det))
        data = mycursor.fetchall()

        mycursor.execute("SELECT count(*) FROM cs_search where uname=%s && keyword=%s",(uname,getval))
        cnt2 = mycursor.fetchone()[0]
        if cnt2==0:

            mycursor.execute("SELECT max(id)+1 FROM cs_search")
            maxid1 = mycursor.fetchone()[0]
            if maxid1 is None:
                maxid1=1
                
            sql = "INSERT INTO cs_search(id, uname, keyword, scount) VALUES (%s, %s, %s, %s)"
            val = (maxid1, uname, getval, '1')
            mycursor.execute(sql,val)
            mydb.commit()
        else:
            mycursor.execute('update cs_search set scount=scount+1 WHERE uname=%s && keyword=%s', (uname,getval))
            mydb.commit()

        
    elif cc=="1":
        mycursor.execute("SELECT * FROM cs_product where category=%s order by star desc",(cat,))
        data = mycursor.fetchall()
    else:
        mycursor.execute("SELECT * FROM cs_product order by star desc")
        data = mycursor.fetchall()

    import datetime
    now = datetime.datetime.now()
    rdate=now.strftime("%d-%m-%Y")
    
    if act=="cart":
        pid = request.args.get('pid')
        mycursor.execute('SELECT count(*) FROM cs_cart WHERE uname=%s && pid = %s && status=0', (uname, pid))
        num = mycursor.fetchone()[0]

        mycursor.execute("SELECT * FROM cs_product where id=%s",(pid,))
        pdata = mycursor.fetchone()
        price=pdata[3]
        cat=pdata[1]
        if num==0:
            mycursor.execute("SELECT max(id)+1 FROM cs_cart")
            maxid = mycursor.fetchone()[0]
            if maxid is None:
                maxid=1

            pc=0
            if poffer=="yes":
                mycursor.execute("SELECT * FROM cs_offer where offer_type=%s",(uff,))
                rf1 = mycursor.fetchone()
                per=rf1[4]
                dc=(price/100)*per
                fprice=price-dc
                pc=fprice
            else:
                pc=price
                
                
            sql = "INSERT INTO cs_cart(id, uname, pid, status, rdate, price,category) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            val = (maxid, uname, pid, '0', rdate, pc, cat)
            mycursor.execute(sql,val)
            mydb.commit()
            return redirect(url_for('userhome'))

    mycursor.execute("SELECT count(*) FROM cs_cart where uname=%s && status=0",(uname,))
    cnt = mycursor.fetchone()[0]
    if cnt>0:
        msg="1"
    else:
        msg=""
    
    return render_template('userhome.html',msg=msg,usr=usr,data=data,cnt=cnt,data2=data2,mess=mess,email=email,msg2=msg2,offer=offer,per=per,off_mess=off_mess)

@app.route('/cart', methods=['GET', 'POST'])
def cart():
    act=""
    pid=""
    did=""
    amount=""
    if 'username' in session:
        uname = session['username']

    cursor = mydb.cursor()
    cursor.execute("SELECT count(*) FROM cs_cart where uname=%s && status=0",(uname, ))
    cnt = cursor.fetchone()[0]
    if cnt>0:
        act="1"
    else:
        act=""
    
    cursor.execute('SELECT c.id,p.product,c.price,p.detail,p.photo,c.rdate FROM cs_cart c,cs_product p where c.pid=p.id and c.uname=%s and c.status=0', (uname, ))
    data = cursor.fetchall()

    cursor.execute("SELECT * FROM cs_cart where uname=%s && status=0",(uname, ))
    dr = cursor.fetchall()
    amt=0
    for dv in dr:
        pid=dv[2]
        cursor.execute("SELECT price FROM cs_product where id=%s",(pid, ))
        pr = cursor.fetchone()[0]
        amt+=dv[6]
        

    
    '''if request.method=='GET':
        act = request.args.get('act')
        pid = request.args.get('pid')
        did = request.args.get('did')
        if act=="ok":
            mycursor = mydb.cursor()
            mycursor.execute("SELECT max(id)+1 FROM cs_cart")
            maxid = mycursor.fetchone()[0]
            if maxid is None:
                maxid=1
            now = datetime.datetime.now()
            rdate=now.strftime("%d-%m-%Y")
            
            sql = "INSERT INTO cart(id, uname, pid, rdate) VALUES (%s, %s, %s, %s)"
            val = (maxid, uname, pid, rdate)
            mycursor.execute(sql,val)
            mydb.commit()
            return redirect(url_for('cart',data=data))
        if act=="del":
            cursor = mydb.cursor()
            cursor.execute('delete FROM cart WHERE id = %s', (did, ))
            mydb.commit()
            return redirect(url_for('cart',data=data))'''

    if request.method=='POST':
        amount=request.form['amount']
        print("test")
        return redirect(url_for('payment', amount=amt))
            
    return render_template('cart.html', data=data, amount=amt,act=act)


@app.route('/payment', methods=['GET', 'POST'])
def payment():
    msg=""
    mob2=""
    email2=""
    uname=""
    amount=0
    message=""
    st=""
    if 'username' in session:
        uname = session['username']
    if request.method=='GET':
        amount = request.args.get('amount')

    import datetime
    now = datetime.datetime.now()
    rdate=now.strftime("%d-%m-%Y")
    cursor = mydb.cursor()

    #print("uname="+uname)
    cursor.execute("SELECT * FROM cs_register where uname=%s",(uname, ))
    rd=cursor.fetchone()
    name=rd[1]
    mob1=rd[2]
    email=rd[3]

    x=0
    if request.method=='POST':
        card=request.form['card']
        amount=request.form['amount']
        

        cursor.execute("SELECT * FROM cs_register where uname=%s",(uname, ))
        rr=cursor.fetchone()
        mob2=rr[3]
        email2=rr[4]
        
        cursor.execute("SELECT max(id)+1 FROM cs_purchase")
        maxid = cursor.fetchone()[0]
        if maxid is None:
            maxid=1

        st="1"
        message="Dear "+name+", Amount Rs."+amount+" Purchased Success, Recommended Products - Click http://localhost:5000/recommend1?user="+uname
        #url="http://iotcloud.co.in/testmail/sendmail.php?email="+email+"&message="+message
        #webbrowser.open_new(url)

        cursor.execute('update cs_cart set status=1,bill_id=%s WHERE uname=%s && status=0', (maxid, uname ))
        mydb.commit()

        sql = "INSERT INTO cs_purchase(id, uname, amount, rdate) VALUES (%s, %s, %s, %s)"
        val = (maxid, uname, amount, rdate)
        cursor.execute(sql,val)
        mydb.commit()
        msg="1"

        

    return render_template('payment.html', msg=msg, amount=amount,mess=message,email=email,st=st)


@app.route('/purchase', methods=['GET', 'POST'])
def purchase():
    uname=""
    amount=0
    if 'username' in session:
        uname = session['username']
    
    
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM cs_purchase where uname=%s",(uname, ))
    data1=cursor.fetchall()

    return render_template('purchase.html', data1=data1)

@app.route('/view', methods=['GET', 'POST'])
def view():
    uname=""
    amount=0
    if 'username' in session:
        uname = session['username']
    
    bid = request.args.get('bid')
    cursor = mydb.cursor()
    cursor.execute('SELECT c.id,p.product,c.price,p.detail,p.photo,c.rdate FROM cs_cart c,cs_product p where c.pid=p.id and c.bill_id=%s', (bid, ))
    data = cursor.fetchall()

    return render_template('view.html', data=data)

@app.route('/view_review', methods=['GET', 'POST'])
def view_review():
    msg=""
    uname=""
    rid=""
    data=[]
    pst=""
    dg1=""
    dg2=""
    dg3=""
    pst=""
    pid = request.args.get('pid')
    if 'username' in session:
        uname = session['username']
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM cs_register where uname=%s",(uname,))
    usr = mycursor.fetchone()

    mycursor.execute("SELECT * FROM cs_product where id=%s",(pid,))
    prd = mycursor.fetchone()

    i=0
    df = pd.read_csv('static/dataset/dataset_review.csv')
    for dd in df.values:
        prid="PROD00"+str(pid)
        if dd[1]==prid:
            if i<10:
                data.append(dd)

            i+=1

    ff=open("static/data1.txt","r")
    dv1=ff.read()
    ff.close()
    dv11=dv1.split("|")

    ff=open("static/data2.txt","r")
    dv2=ff.read()
    ff.close()
    dv22=dv2.split("|")

    ff=open("static/data3.txt","r")
    dv3=ff.read()
    ff.close()
    dv33=dv3.split("|")

    if int(pid)<6:
        pst="1"
        pp=int(pid)
        dg1=dv11[pp]
        dg2=dv22[pp]
        dg3=dv33[pp]
    
    return render_template('view_review.html', prd=prd,data=data,dv11=dv11,dg1=dg1,dg2=dg2,dg3=dg3,pst=pst)


@app.route('/add_review', methods=['GET', 'POST'])
def add_review():
    msg=""
    act=""
    message=""
    uname=""
    rid=""
    rdata=[]
    pid = request.args.get('pid')
    if 'username' in session:
        uname = session['username']
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM cs_register where uname=%s",(uname,))
    usr = mycursor.fetchone()
    email=usr[3]
    name=usr[1]

    mycursor.execute("SELECT * FROM cs_product where id=%s",(pid,))
    prd = mycursor.fetchone()

    import datetime
    now = datetime.datetime.now()
    rdate=now.strftime("%d-%m-%Y")
    
    mycursor.execute("SELECT count(*) FROM cs_review where pid=%s && status=1",(pid,))
    cnt = mycursor.fetchone()[0]
    if cnt>0:
        act="1"
    mycursor.execute("SELECT * FROM cs_review where pid=%s && status=1",(pid,))
    data1 = mycursor.fetchall()

    rn=randint(10000,99999)

    if request.method=='POST':
        star=request.form['star']
        review=request.form['review']
        mycursor.execute("SELECT max(id)+1 FROM cs_review")
        maxid = mycursor.fetchone()[0]
        if maxid is None:
            maxid=1
            
        sql = "INSERT INTO cs_review(id,pid,uname,review,star,rdate,status,review_code) VALUES (%s, %s, %s, %s, %s,%s,%s,%s)"
        val = (maxid,pid,uname,review,star,rdate,'0',str(rn))
        mycursor.execute(sql,val)
        mydb.commit()
        #msg="Your Review has sent.."
        message="Dear "+name+", Review Code: "+str(rn)
        #url="http://iotcloud.co.in/testmail/sendmail.php?email="+email+"&message="+message
        #webbrowser.open_new(url)
        #msg="1"
        
        #
        pid=str(maxid)
        mycursor.execute("SELECT * FROM cs_review where pid=%s && status=1",(pid,))
        pdd = mycursor.fetchall()
        sr=0
        i=0
        for pn in pdd:
            sr+=pn[4]
            i+=1
        if i>0:
            ss=sr/i
            star=int(ss)
            mycursor.execute('update cs_product set star=%s WHERE id = %s', (star,pid))
            mydb.commit()
        #
        df = pd.read_csv('static/dataset/dataset_review.csv')
        for dd in df.values:
            dt=[]
            prid="PROD00"+str(pid)
            if dd[3]==review:
                dt.append(dd[4])
                dt.append(dd[5])
                dt.append(dd[6])
                rdata.append(dt)
                break

                
        #
        msg="ok"
        rid=str(maxid)
        #return redirect(url_for('review_code',rid=maxid))
        

    return render_template('add_review.html',msg=msg,usr=usr,data1=data1,act=act,pid=pid,prd=prd,mess=message,email=email,rid=rid,rdata=rdata)

@app.route('/review_code', methods=['GET', 'POST'])
def review_code():
    msg=""
    uname=""
    rid = request.args.get('rid')
    if 'username' in session:
        uname = session['username']
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM cs_register where uname=%s",(uname,))
    usr = mycursor.fetchone()
    email=usr[3]
    name=usr[1]

    mycursor.execute("SELECT * FROM cs_review where id=%s",(rid,))
    data1 = mycursor.fetchone()
    code=data1[7]
    pid=data1[1]
    if request.method=='POST':
        rcode=request.form['review_code']
        if rcode==code:
            mycursor.execute("SELECT count(*) FROM cs_cart where pid=%s && uname=%s && status=1",(pid,uname))
            cnt = mycursor.fetchone()[0]
            if cnt>0:
                mycursor.execute('update cs_review set status=1 WHERE id = %s', (rid,))
                mydb.commit()

                mycursor.execute("SELECT * FROM cs_review where pid=%s && status=1",(pid,))
                pdd = mycursor.fetchall()
                sr=0
                i=0
                for pn in pdd:
                    sr+=pn[4]
                    i+=1
                ss=sr/i
                star=int(ss)
                mycursor.execute('update cs_product set star=%s WHERE id = %s', (star,pid))
                mydb.commit()
                    
            
                msg="Your Review has posted"
            else:
                msg="Your Review has not posted! not buy this product!"
        else:
            msg="Review Code wrong!"


            
    return render_template('review_code.html',msg=msg)

@app.route('/search', methods=['GET', 'POST'])
def search():
    msg=""
    cnt=0
    uname=""
    act = request.args.get('act')
    cat = request.args.get('cat')
    if 'username' in session:
        uname = session['username']
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM cs_register where uname=%s",(uname,))
    usr = mycursor.fetchone()

    mycursor.execute("SELECT * FROM cs_search where uname=%s order by scount desc",(uname,))
    data2 = mycursor.fetchall()

    cc=""
    if cat is None:
        cc=""
    else:
        cc="1"

    if cc=="1":
        cat="%"+cat+"%"
        prd="%"+cat+"%"
        det="%"+cat+"%"
        mycursor.execute("SELECT * FROM cs_product where category like %s || product like %s || detail like %s  order by star desc",(cat,prd,det))
        data = mycursor.fetchall()
    else:
        mycursor.execute("SELECT * FROM cs_product order by star desc")
        data = mycursor.fetchall()

    now = datetime.datetime.now()
    rdate=now.strftime("%d-%m-%Y")
    
    if act=="cart":
        pid = request.args.get('pid')
        mycursor.execute('SELECT count(*) FROM cs_cart WHERE uname=%s && pid = %s && status=0', (uname, pid))
        num = mycursor.fetchone()[0]

        mycursor.execute("SELECT * FROM cs_product where id=%s",(pid,))
        pdata = mycursor.fetchone()
        price=pdata[3]
        cat=pdata[1]
        if num==0:
            mycursor.execute("SELECT max(id)+1 FROM cs_cart")
            maxid = mycursor.fetchone()[0]
            if maxid is None:
                maxid=1
                
            sql = "INSERT INTO cs_cart(id, uname, pid, status, rdate, price,category) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            val = (maxid, uname, pid, '0', rdate, price, cat)
            mycursor.execute(sql,val)
            mydb.commit()
            return redirect(url_for('search'))

    mycursor.execute("SELECT count(*) FROM cs_cart where uname=%s && status=0",(uname,))
    cnt = mycursor.fetchone()[0]
    if cnt>0:
        msg="1"
    else:
        msg=""
    
    return render_template('search.html',msg=msg,usr=usr,data=data,cnt=cnt,data2=data2)


@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    msg=""
    cnt=0
    uname=""
    act = request.args.get('act')
    cat = request.args.get('cat')
    if 'username' in session:
        uname = session['username']
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM cs_register where uname=%s",(uname,))
    usr = mycursor.fetchone()
    oftype=usr[7]

    mycursor.execute("SELECT * FROM cs_offer where offer_type=%s",(oftype,))
    fd1 = mycursor.fetchone()
    offer=fd1[1]
    per=fd1[4]
    
    mycursor.execute("SELECT * FROM admin where username='admin'")
    usr2 = mycursor.fetchone()
    min_count=usr2[2]

    mycursor.execute("SELECT * FROM cs_product")
    pdata = mycursor.fetchall()
    prdd=[]
    for pr in pdata:

        mycursor.execute("SELECT count(*) FROM cs_cart where pid=%s",(pr[0],))
        pp1 = mycursor.fetchone()[0]
        if pp1<=min_count:
            prdd.append(pr[0])
    data=[] 
    for pv in prdd:
        mycursor.execute("SELECT * FROM cs_product where id=%s order by star desc",(pv,))
        data1 = mycursor.fetchall()
        for rd1 in data1:
            dat=[]
            dat.append(rd1[0])
            dat.append(rd1[1])
            dat.append(rd1[2])
            dat.append(rd1[3])
            dat.append(rd1[4])
            dat.append(rd1[5])
            dat.append(rd1[6])

            dc=(rd1[3]/100)*per
            fprice=rd1[3]-dc
            dat.append(fprice)
            data.append(dat)
        
 
    
    return render_template('recommend.html',msg=msg,usr=usr,data=data,offer=offer,per=per)

@app.route('/recommend1', methods=['GET', 'POST'])
def recommend1():
    msg=""
    cnt=0
    uname=""
    act = request.args.get('act')
    user = request.args.get('user')
    
    
    if 'username' in session:
        uname = session['username']
    else:
        session['username'] = user
        uname=user
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM cs_register where uname=%s",(uname,))
    usr = mycursor.fetchone()
    oftype=usr[7]

    mycursor.execute("SELECT * FROM cs_offer where offer_type=%s",(oftype,))
    fd1 = mycursor.fetchone()
    offer=fd1[1]
    per=fd1[4]
    
    mycursor.execute("SELECT * FROM admin where username='admin'")
    usr2 = mycursor.fetchone()
    min_count=usr2[2]

    mycursor.execute("SELECT * FROM cs_product")
    pdata = mycursor.fetchall()
    prdd=[]
    for pr in pdata:

        mycursor.execute("SELECT count(*) FROM cs_cart where pid=%s",(pr[0],))
        pp1 = mycursor.fetchone()[0]
        if pp1<=min_count:
            prdd.append(pr[0])
    data=[] 
    for pv in prdd:
        mycursor.execute("SELECT * FROM cs_product where id=%s order by star desc",(pv,))
        data1 = mycursor.fetchall()
        for rd1 in data1:
            dat=[]
            dat.append(rd1[0])
            dat.append(rd1[1])
            dat.append(rd1[2])
            dat.append(rd1[3])
            dat.append(rd1[4])
            dat.append(rd1[5])
            dat.append(rd1[6])

            dc=(rd1[3]/100)*per
            fprice=rd1[3]-dc
            dat.append(fprice)
            data.append(dat)
    
    return render_template('recommend1.html',msg=msg,usr=usr,data=data,offer=offer,per=per)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    msg=""

        
    return render_template('admin.html',msg=msg)

@app.route('/load_data', methods=['GET', 'POST'])
def load_data():
    msg=""
    cnt=0
    filename = 'static/dataset/dataset.csv'
    data1 = pd.read_csv(filename, header=0)
    data2 = list(data1.values.flatten())
    data=[]
    i=0
    sd=len(data1)
    rows=len(data1.values)
    
    #print(str(sd)+" "+str(rows))
    for ss in data1.values:
        cnt=len(ss)
        if i<200:        
            data.append(ss)
        i+=1
    cols=cnt
    #if request.method=='POST':
    #    return redirect(url_for('preprocess'))
    return render_template('load_data.html',data=data, msg=msg, rows=rows, cols=cols)

stop_words = set(stopwords.words('english'))
ps = PorterStemmer()

# Function to preprocess reviews
def preprocess_review(review):
    # Convert to lowercase
    review = review.lower()

    # Remove punctuation and numbers
    review = re.sub(r'[^a-zA-Z\s]', '', review)

    # Tokenize the review
    tokens = word_tokenize(review)

    # Remove stopwords
    tokens = [word for word in tokens if word not in stop_words]

    # Stem the words
    tokens = [ps.stem(word) for word in tokens]

    # Return the processed review as a space-separated string
    return ' '.join(tokens)

@app.route('/preprocess', methods=['GET', 'POST'])
def preprocess():
    msg=""
    mem=0
    cnt=0
    cols=0
    filename = 'static/dataset/dataset.csv'
    df = pd.read_csv(filename)
    #stop_words = stopwords.words('english')
    stop_words = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't",',','.','I','\'','-','/']
    ##Tokenize
    data1=[]
    i=0
    for ds in df.values:
        dt=[]
        if i<5:
            
            dt.append(ds[3])
            text=ds[3]

            #doc = nlp(text)
            text_tokens=text.split(" ")
            
            #text_tokens = [token.text for token in doc]
            #text_tokens=tokenize_by_word(text)
            #text_tokens =word_tokenize(text)
            tokens_without_sw = [word for word in text_tokens if not word in stop_words]
            dt.append(tokens_without_sw)

            
            data1.append(dt)
        i+=1

    #Stemming
    ps = PorterStemmer()
     
    # choose some words to be stemmed
    #words = ["program", "programs", "programmer", "programming", "programmers"]
     
    
    data2=[]
    i=0
    for ds2 in df.values:
        dt2=[]
        if i<5:
            
            
            text2=ds2[3]
            dt2.append(ds2[3])

            #doc = nlp(text)
            
            text_tokens=text2.split(" ")
           
            #text_tokens = [token.text for token in doc]
            #text_tokens =word_tokenize(text2)
            tokens_without_sw = [word for word in text_tokens if not word in stop_words]
            
            swrd=[]
            for w in tokens_without_sw:
                sw=ps.stem(w)
                swrd.append(sw)
            dt2.append(swrd)

            
            data2.append(dt2)
        i+=1
    ##Stop words

    stopwords = [ "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "could", "did", "do", "does", "doing", "down", "during", "each", "few", "for", "from", "further", "had", "has", "have", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "it", "it's", "its", "itself", "let's", "me", "more", "most", "my", "myself", "nor", "of", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "she", "she'd", "she'll", "she's", "should", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "we", "we'd", "we'll", "we're", "we've", "were", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "would", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves" ]
    #data = "All work and no play makes jack dull boy. All work and no play makes jack a dull boy."
    data3=[]
    i=0
    for ds3 in df.values:
        dt3=[]
        if i<5:
            
            
            content=ds3[3]
            
            
            dt3.append(ds3[3])
            content = content.lower()
            swrd=[]
            # Remove stop words
            for stopword in stopwords:
                content = content.replace(stopword + " ", "")
                content = content.replace(" " + stopword, "")
                swrd.append(content)
            data3.append(swrd)
        i+=1
    

    
    return render_template('preprocess.html',data1=data1,data2=data2,data3=data3)

#BERT
def BERT():
    # Load CSV
    df = pd.read_csv('static/dataset/dataset.csv')

    # Only needed columns
    df = df[['Customer ID', 'Product ID', 'Review']]

    df = df.head()

    # Load BERT model (small, fast model)
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Encode Reviews to BERT embeddings
    embeddings = model.encode(df['Review'].tolist())

    # Convert embeddings to DataFrame
    bert_df = pd.DataFrame(embeddings)

    # Add Customer ID and Product ID back
    bert_df['Customer ID'] = df['Customer ID']
    bert_df['Product ID'] = df['Product ID']

def work(self, inp, seg=None, layers=None):
   
    if layers is not None:
        tot_layers = len(self.layers)
        for x in layers:
            if not (-tot_layers <= x < tot_layers):
                raise ValueError('layer %d out of range '%x)
        layers = [ (x+tot_layers if x <0 else x) for x in layers]
        max_layer_id = max(layers)
    
    seq_len, bsz = inp.size()
    if seg is None:
        seg = torch.zeros_like(inp)
    x = self.tok_embed(inp) + self.seg_embed(seg) + self.pos_embed(inp)
    x = self.emb_layer_norm(x)
    x = F.dropout(x, p=self.dropout, training=self.training)
    padding_mask = torch.eq(inp, self.vocab.padding_idx)
    if not padding_mask.any():
        padding_mask = None
    
    xs = []
    for layer_id, layer in enumerate(self.layers):
        x, _ ,_ = layer(x, self_padding_mask=padding_mask)
        xs.append(x)
        if layers is not None and layer_id >= max_layer_id:
            break
    
    if layers is not None:
        x = torch.stack([xs[i] for i in layers])
        z = torch.tanh(self.one_more_nxt_snt(x[:,0,:,:]))
    else:
        z = torch.tanh(self.one_more_nxt_snt(x[0]))
    return x, z

def forward(self, truth, inp, seg, msk, nxt_snt_flag):
    seq_len, bsz = inp.size()
    x = self.tok_embed(inp) + self.seg_embed(seg) + self.pos_embed(inp)
    x = self.emb_layer_norm(x)
    x = F.dropout(x, p=self.dropout, training=self.training)
    padding_mask = torch.eq(truth, self.vocab.padding_idx)
    if not padding_mask.any():
        padding_mask = None
    for layer in self.layers:
        x, _ ,_ = layer(x, self_padding_mask=padding_mask)

    masked_x = x.masked_select(msk.unsqueeze(-1))
    masked_x = masked_x.view(-1, self.embed_dim)
    gold = truth.masked_select(msk)
    
    y = self.one_more_layer_norm(gelu(self.one_more(masked_x)))
    out_proj_weight = self.tok_embed.weight

    if self.approx is None:
        log_probs = torch.log_softmax(F.linear(y, out_proj_weight, self.out_proj_bias), -1)
    else:
        log_probs = self.approx.log_prob(y)

    loss = F.nll_loss(log_probs, gold, reduction='mean')

    z = torch.tanh(self.one_more_nxt_snt(x[0]))
    nxt_snt_pred = torch.sigmoid(self.nxt_snt_pred(z).squeeze(1))
    nxt_snt_acc = torch.eq(torch.gt(nxt_snt_pred, 0.5), nxt_snt_flag).float().sum().item()
    nxt_snt_loss = F.binary_cross_entropy(nxt_snt_pred, nxt_snt_flag.float(), reduction='mean')
    
    tot_loss = loss + nxt_snt_loss
    
    _, pred = log_probs.max(-1)
    tot_tokens = msk.float().sum().item()
    acc = torch.eq(pred, gold).float().sum().item()
    
    return (pred, gold), tot_loss, acc, tot_tokens, nxt_snt_acc, bsz

@app.route('/feature', methods=['GET', 'POST'])
def feature():
    msg=""
    cnt=0
    filename = 'static/dataset/dataset.csv'
    df = pd.read_csv(filename)
    df = df.head(10)

    df = df[['Customer ID', 'Product ID', 'Review']]

    # TF-IDF Vectorization
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(df['Review'])

    # Convert TF-IDF result to a DataFrame
    tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=vectorizer.get_feature_names_out())

    # Optionally add Customer ID and Product ID for clarity
    tfidf_df['Customer ID'] = df['Customer ID']
    tfidf_df['Product ID'] = df['Product ID']
    data_tfidf = tfidf_df.to_dict(orient='records')
    features = vectorizer.get_feature_names_out()
   
    return render_template('feature.html',msg=msg,data_tfidf=data_tfidf, features=features)

#BiDAGNN - Review Classification 
class BiDAGNN():
    def __init__(self, in_channels, hidden_channels, out_channels, heads=1):
        super(BiDAGNN, self).__init__()
        
        # First layer: Attention GNN layer (forward)
        self.gat_forward = GATConv(in_channels, hidden_channels, heads=heads, concat=True)
        
        # Second layer: Attention GNN layer (backward)
        self.gat_backward = GATConv(in_channels, hidden_channels, heads=heads, concat=True)
        
        # Final Linear layer
        self.fc = torch.nn.Linear(2 * hidden_channels * heads, out_channels)  # 2x because forward + backward concat

    def forward(self, x, edge_index):
        # Forward message passing
        out_forward = self.gat_forward(x, edge_index)

        # Backward message passing (reverse edges)
        edge_index_reversed = torch.stack([edge_index[1], edge_index[0]], dim=0)
        out_backward = self.gat_backward(x, edge_index_reversed)

        # Concatenate forward and backward features
        out = torch.cat([out_forward, out_backward], dim=1)

        # Pass through final FC layer
        out = self.fc(out)
        
        return out

    
@app.route('/classify', methods=['GET', 'POST'])
def classify():
    msg=""
    cnt=0
    data=[]


    df = pd.read_csv('static/dataset/dataset_review.csv')
    #Text Preprocessing
    df['Clean_Review'] = df['Review'].str.lower()

    #Sentiment Analysis 
    def get_sentiment(text):
        analysis = TextBlob(text)
        if analysis.sentiment.polarity > 0:
            return "Positive"
        elif analysis.sentiment.polarity < 0:
            return "Negative"
        else:
            return "Neutral"

    df['Predicted_Sentiment'] = df['Clean_Review'].apply(get_sentiment)


    ##Sentiment Distribution
    plt.figure(figsize=(6,4))
    sns.countplot(data=df, x='Sentiment', palette='viridis')
    plt.title('Original Sentiment Distribution')
    plt.xlabel('Sentiment')
    plt.ylabel('Number of Reviews')
    #plt.savefig('static/graph/g1.png')
    #plt.show()

    ##Predicted vs Original Sentiment
    plt.figure(figsize=(6,4))
    sns.countplot(data=df, x='Predicted_Sentiment', palette='coolwarm')
    plt.title('Predicted Sentiment Distribution')
    plt.xlabel('Predicted Sentiment')
    plt.ylabel('Number of Reviews')
    #plt.savefig('static/graph/g2.png')
    #plt.show()

    ##Word Clouds for Positive and Negative Aspects
    positive_text = " ".join(df['Positive Aspect Terms'].dropna().tolist())
    negative_text = " ".join(df['Negative Aspect Terms'].dropna().tolist())

    wordcloud_pos = WordCloud(width=800, height=400, background_color='white', colormap='Greens').generate(positive_text)
    wordcloud_neg = WordCloud(width=800, height=400, background_color='white', colormap='Reds').generate(negative_text)

    # Positive Aspects
    plt.figure(figsize=(10,5))
    plt.imshow(wordcloud_pos, interpolation='bilinear')
    plt.axis('off')
    plt.title('Positive Aspects WordCloud')
    #plt.savefig('static/graph/g3.png')
    #plt.show()

    # Negative Aspects
    plt.figure(figsize=(10,5))
    plt.imshow(wordcloud_neg, interpolation='bilinear')
    plt.axis('off')
    plt.title('Negative Aspects WordCloud')
    #plt.savefig('static/graph/g4.png')
    #plt.show()

    ##################
    # Group by Product and Sentiment
    product_sentiment_counts = df.groupby(['Product ID', 'Sentiment']).size().reset_index(name='Count')

    # Set the figure size
    plt.figure(figsize=(14, 7))

    # Create a grouped barplot
    sns.barplot(data=product_sentiment_counts, x='Product ID', y='Count', hue='Sentiment', palette='Set2')

    # Improve plot
    plt.title('Sentiment Distribution per Product', fontsize=18)
    plt.xlabel('Product', fontsize=14)
    plt.ylabel('Number of Reviews', fontsize=14)
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Sentiment')
    plt.tight_layout()
    #plt.savefig('static/graph/g5.png')
    #################
    # Check column names
    print(df.columns.tolist())

    # Group by Product and Sentiment to count
    product_sentiment_counts = df.groupby(['Product ID', 'Sentiment']).size().reset_index(name='Count')

    # Calculate total reviews per product
    total_reviews_per_product = product_sentiment_counts.groupby('Product ID')['Count'].transform('sum')

    # Add a 'Percentage' column
    product_sentiment_counts['Percentage'] = (product_sentiment_counts['Count'] / total_reviews_per_product) * 100

    # Set the figure size
    plt.figure(figsize=(14, 7))

    # Create a grouped barplot based on Percentage
    sns.barplot(data=product_sentiment_counts, x='Product ID', y='Percentage', hue='Sentiment', palette='Set2')

    # Improve plot
    plt.title('Sentiment Percentage Distribution per Product', fontsize=18)
    plt.xlabel('Product', fontsize=14)
    plt.ylabel('Percentage of Reviews (%)', fontsize=14)
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Sentiment')
    plt.tight_layout()
    #plt.savefig('static/graph/g6.png')
    # Show plot
    ############
    # Calculate counts
    sentiment_counts = df.groupby(['Product ID', 'Sentiment']).size().unstack(fill_value=0)

    # Calculate percentages
    sentiment_percentages = sentiment_counts.div(sentiment_counts.sum(axis=1), axis=0) * 100

    # Plot
    sentiment_percentages.plot(kind='bar', stacked=True, figsize=(14, 7), colormap='Set2')

    # Improve plot
    plt.title('Sentiment Distribution per Product (100% Stacked)', fontsize=18)
    plt.ylabel('Percentage (%)', fontsize=14)
    plt.xlabel('Product', fontsize=14)
    plt.legend(title='Sentiment', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    #plt.savefig('static/graph/g7.png')

    return render_template('classify.html',data=data, msg=msg)



##########################
@app.route('/logout')
def logout():
    # remove the username from the session if it is there
    session.pop('username', None)
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)


