# -*- coding: utf-8 -*-
"""
Created on Thu Jul 16 20:37:04 2020

@author: Anand
"""

import requests, random, webbrowser

from datetime import date, timedelta,datetime
import mysql.connector as sqltor
import matplotlib.pyplot as plt
import os       

#Converts the reference currency to USD from EUR
#Returns a big nested dictionary
def convertToUSD(lst):
    lst['base'] = 'USD'
    n = lst['rates']['USD']
    for keys in lst['rates']:
        lst['rates'][keys]/=n
    lst['rates']['EUR']=1/n
    return lst

#Calls the API Endpoint and retrieves data, converts it from JSON to Python dict
#Returns a dictionary
def callAPI(url):
    r = requests.get(url).json()
    return r

#Converts a string having hyphens to underscores
#Returns that string    
def convertDateToUnderscore(num):
    str1 = num
    str2 = ''
    for i in range(len(str1)):
        if str1[i] != '-':
            str2+=str1[i]
        else:
            str2+='_'
    return str2

mycon = sqltor.connect(host = 'localhost',user = "root",passwd = 'Pressing.123',database = 'dbtest')
if mycon.is_connected() == False:
    print("Error connecting to database")
else:
    print("Successfully connected")
cursor = mycon.cursor()

#Creates a table currcountries, if it does not exist 
#Calls an API, which provides info regarding each country(Some info is wrong, is changed inside the function)
#Void function, returns None
def currcountries():
    cursor.execute('''SELECT TABLE_NAME FROM information_schema.columns WHERE TABLE_NAME = "currcountries"''')
    r = cursor.fetchall()
    if len(r) != 0:
        return
    counturl = "http://countryapi.gear.host/v1/Country/getCountries"
    resujson = callAPI(counturl)
    cursor.execute("create table IF NOT EXISTS currcountries(Name varchar(100) PRIMARY KEY,CurrencyCode varchar(10), CurrencyName varchar(100),Region varchar(20))")
    mycon.commit()
    for dct in resujson['Response']:
        cursor.execute('''insert ignore into currcountries values("{0}","{1}","{2}","{3}")'''.format(dct["Name"],dct["CurrencyCode"],dct["CurrencyName"],dct["Region"]))
        mycon.commit()
    cursor.execute('''UPDATE currcountries 
                   SET CurrencyCode = 'SGD',CurrencyName = 'Singapore Dollar' 
                   WHERE Name = 'Singapore' ''')
    cursor.execute('''UPDATE currcountries 
                   SET CurrencyCode = 'IMP',CurrencyName = 'Isle of Man Pound' 
                   WHERE Name = 'Isle of Man' ''')
    cursor.execute('''UPDATE currcountries 
                   SET CurrencyCode = 'JEP',CurrencyName = 'Jersey Pound' 
                   WHERE Name = 'Jersey' ''')
    cursor.execute("insert ignore into currcountries values('Bitcoin','BTC','Bitcoin','Cryptocurrency')")
    cursor.execute("insert ignore into currcountries values('Chilean Unit of Account','CLF','Chilean Unit of Account','Americas')")    
    cursor.execute("insert ignore into currcountries values('Cuban Peso','CUP','Cuban Peso','Americas')")
    cursor.execute("insert ignore into currcountries values('Silver','XAG','Silver Ounce','Metal')")
    cursor.execute("insert ignore into currcountries values('Gold','XAU','Gold Ounce','Metal')")
    cursor.execute("DELETE FROM currcountries WHERE Name = 'South Sudan'")
    mycon.commit()
    
#Returns a dictionary in which keys are currency codes and values are the latest currency values
def getDictionaryLatest():
    d = {}
    cursor.execute('''SELECT * from currvalues''')
    data = cursor.fetchall()
    for i in range(len(data)):
        d[data[i][0]] = data[i][1]
    mycon.commit()    
    return d
d = getDictionaryLatest()

#Returns the currency code for each country
def getCurrCode(country):
    country = country.capitalize()
    cursor.execute("select CurrencyCode from currcountries where Name like '{0}'".format(country))
    code = cursor.fetchone()[0]
    return code

#Returns the latest currency value for each country
def getCurrCodeLatest(country):
    country = country.capitalize()
    cursor.execute("select CurrencyCode from currcountries where Name like '{0}'".format(country))
    code = cursor.fetchone()[0]
    cursor.execute("select CurrFactorLatest from currvalues where CurrCode = '{0}'".format(code))
    value = cursor.fetchone()[0]
    return value

#Takes startdate and enddate datetime objects, also optional gaps and limits
#Returns a list of date strings in YYYY-MM-DD between the startdate and enddate(both inclusive)
def listOfDays(startdate,enddate = date.today(),gap = 1,limit = 500):   
    delta1 = enddate - startdate
    list1 = []
    if delta1.days//gap >limit:
        print("No of days is too large, not supported by this function")
        return []
    start_date = startdate
    end_date = enddate
    delta = timedelta(days=gap)
    while start_date <= end_date:
        list1.append(start_date.strftime("%Y-%m-%d"))
        start_date += delta
    return list1

#Takes a numeric value and a datetime object
#Returns a list of date strings in YYYY-MM-DD from the enddate till the length is limit + 1
def daysListFromDate(limit, enddate = date.today()): 
    if type(limit) != int:
        print("The argument should be of int datatype")
        return []
    if limit > 50:
        print("The no of values is too high")
        return []
    list1 = []
    for i in range(limit + 1):
        list1.append((enddate - timedelta(days=i)).strftime("%Y-%m-%d"))
    list1.reverse()
    return list1

#Changes datetime objects to date strings and to YYYY-MM-DD format
#Returns the date string
def datetimeToString(date):
    datestr = date.strftime("%Y-%m-%d")
    return datestr

#Changes date strings in DD-MM-YYYY format to datetime objects
#Returns the date of the datetime object
def stringToDatetime(date_str):    
    format_str = '%d-%m-%Y' 
    datetime_obj = datetime.strptime(date_str, format_str)
    return datetime_obj.date()

#Takes in the country and the color of the graph
#Graphs the values of the specified country's currency for the last 31 days in the specified color
#Saves it in the images folder
#Returns the location of the image
def saveGraph(country1,color):
    uname = 'Curr31'
    cursor.execute("select CurrencyCode from currcountries where Name like '{0}'".format(country1))
    currcode1 = cursor.fetchone()[0]
    PostgreSQL_select_Query = '''select column_name from information_schema.columns where table_name = '{0}' '''.format(uname)
    cursor.execute(PostgreSQL_select_Query)
    records = cursor.fetchall()
    tup = ('CurrCode',)
    for i in records:
        if i == tup:
            records.remove(i)
    d1 = {}
    for i in range(len(records)):
        cursor.execute('''SELECT {2} from {0} WHERE CurrCode in ('{1}')'''.format(uname,currcode1,records[i][0]))
        data = cursor.fetchall()
        rec = records[i][0]
        d1[rec] = data[0][0]
    
    x1 = list(d1.keys())
    y1 = list(d1.values())
    plt.style.use(['dark_background'])
    plt.rcParams["figure.figsize"] = (10,5)
    plt.plot(x1,y1,color = color)
    plt.xlabel('Date(past month)')
    plt.xticks(x1,rotation = 90)
    plt.ylabel('{0} wrt USD'.format(currcode1))
    plt.title(country1 + " (for the past 31 days)")
    loc = "C:\\Users\\Anand\\Coding\\Images\\{0}-{1}-2-sample.png".format(country1,date.today())
    if os.path.isfile(loc):
        os.remove(loc)   
    plt.savefig(loc,bbox_inches = 'tight', dpi = 300)
    plt.clf()
    plt.close()
    return "file:///C:/Users/Anand/Coding/Images/{0}-{1}-2-sample.png" .format(country1,date.today())
    

def createTable(uname,startdate,enddate):
    startdate = stringToDatetime(startdate)
    enddate = stringToDatetime(enddate)
    dayslst2 = listOfDays(startdate,enddate)
    cursor.execute('''create table IF NOT EXISTS {0}(CurrCode varchar(10) PRIMARY KEY)'''.format(uname))
    mycon.commit()
    startdate1 = startdate.strftime("%Y-%m-%d")
    starturl = 'http://data.fixer.io/api/'+ startdate1 +'?access_key=104d12bf481223711dd4e2e0cf6eaac0'
    startvalues = convertToUSD(callAPI(starturl))
    for key in startvalues['rates']:
        cursor.execute('''insert ignore into {1}(CurrCode) values("{0}")'''.format(key,uname))
        mycon.commit()
    for i in range(len(dayslst2)):
        currhisturl = 'http://data.fixer.io/api/' + dayslst2[i] +'?access_key=104d12bf481223711dd4e2e0cf6eaac0'
        histvalues = callAPI(currhisturl)
        histvaluesrates = convertToUSD(histvalues)
        unddate = convertDateToUnderscore(dayslst2[i])
        try:
            query = '''ALTER TABLE {1}
                    ADD ({0} float)'''
            cursor.execute(query.format(unddate,uname))
            mycon.commit()
            for key in histvaluesrates['rates']:
                query1 = '''UPDATE {3}
                       SET {2} = "{1}"     
                       WHERE CurrCode = "{0}"'''        
                cursor.execute(query1.format(key,histvaluesrates['rates'][key],unddate,uname))
                mycon.commit()
        except:
            for key in histvaluesrates['rates']:
                query1 = '''UPDATE {3}
                       SET {2} = "{1}"     
                       WHERE CurrCode = "{0}"'''        
                cursor.execute(query1.format(key,histvaluesrates['rates'][key],unddate,uname))
                mycon.commit()

#Takes in the user's name, the start and end date strings in DD-MM-YYYY format
#Creates a table if it already does not exist, unique to the user, which has underscore date strings as column names, plus a CurrCode column
#Adds new columns corresponding to the dates in the specified range, both inclusive
#If column is already in the table, does not insert
#If an identical column is available anywhere else in the database, it copies that column to this table
#If the column is not available anywhere else, makes an API call to fetch the data and then writes it into the table
#Is a void function, returns None

def ultimateFunction(uname,startdate,enddate):
    dayslst2 = listOfDays(stringToDatetime(startdate),stringToDatetime(enddate))
    cursor.execute('''create table IF NOT EXISTS {0}(CurrCode varchar(10) PRIMARY KEY)'''.format(uname))
    mycon.commit()
    cursor.execute("SELECT Currcode from currvalues") 
    rc1 = cursor.fetchall() 
    for i in range(len(rc1)):
        cursor.execute('''insert ignore into {1}(CurrCode) values("{0}")'''.format(rc1[i][0],uname))
    cursor.execute("select column_name from information_schema.columns where table_name = '{0}'".format(uname))
    data = cursor.fetchall()
    for i in range(len(dayslst2)):
        unddate = convertDateToUnderscore(dayslst2[i])
        tup = (unddate,)
        cursor.execute("select table_name,column_name from information_schema.columns where column_name = '{0}'".format(unddate))
        data1 = cursor.fetchall()
        dict1 = {}
        for i in range(len(data1)):
            dict1[data1[i][0]] = data1[i][1]
        if unddate in dict1.values():
            if tup not in data:
                tabname = list(dict1.keys())[0]
                query = '''ALTER TABLE {0}
                ADD ({1} float DEFAULT 0.0)'''.format(uname,unddate)
                cursor.execute(query)
                mycon.commit()
                query1 = '''UPDATE {0}
                INNER JOIN {1} ON {0}.CurrCode = {1}.CurrCode 
                SET {0}.{2} = {1}.{2}'''.format(uname,tabname,unddate)
                cursor.execute(query1)
                mycon.commit()    
        if unddate not in dict1.values():
            j = 0
            currhisturl = 'http://data.fixer.io/api/' + dayslst2[i] +'?access_key=104d12bf481223711dd4e2e0cf6eaac0'
            histvaluesrates = convertToUSD(callAPI(currhisturl))
            if j == 0:
                for key in histvaluesrates['rates']:
                    cursor.execute('''insert ignore into {1}(CurrCode) values("{0}")'''.format(key,uname))
                    mycon.commit()
            j+=1
            query = '''ALTER TABLE {1}
            ADD ({0} float DEFAULT 0.00)'''
            cursor.execute(query.format(unddate,uname))
            mycon.commit()
            for key in histvaluesrates['rates']:
                query1 = '''UPDATE {3}
                SET {2} = "{1}"     
                WHERE CurrCode = "{0}"'''        
                cursor.execute(query1.format(key,histvaluesrates['rates'][key],unddate,uname))
                mycon.commit()
                
#Takes in the name, start and end date strings in DD-MM-YYYY format and also the country and the colour required in the graph
#Graphs the currency values for the range of dates specified, with both inclusive, for specified country and colour
#Saves it in the static folder to provide access to Flask
#Returns the time of saving, in HH:MM:SS format

def saveDateGraph(uname,startdate,enddate,country1,color):
    dayslst2 = listOfDays(stringToDatetime(startdate),stringToDatetime(enddate))
    cursor.execute("select CurrencyCode from currcountries where Name like '{0}'".format(country1))
    currcode1 = cursor.fetchone()[0]
    d1 = {}
    for i in range(len(dayslst2)):
        unddate = convertDateToUnderscore(dayslst2[i])
        cursor.execute('''SELECT {2} from {0} WHERE CurrCode in ('{1}')'''.format(uname,currcode1,unddate))
        data = cursor.fetchall()
        d1[unddate] = data[0][0]
    
    x1 = list(d1.keys())
    y1 = list(d1.values())
    plt.style.use(['dark_background'])
    plt.rcParams["figure.figsize"] = (10,5)
    plt.plot(x1,y1,color = color)
    plt.xlabel('Date')
    plt.xticks(x1,rotation = 90)
    plt.ylabel('{0} wrt USD'.format(currcode1))
    plt.title(country1 + " from {0} to {1} ".format(startdate,enddate))
    nowdate = date.today()
    nowtime = datetime.now().strftime("%H-%M-%S")
    loc = "C:\\Users\\Anand\\Coding\\Anand-Test programs\\static\\{1}_{0}_{2}_{3}.png".format(country1,uname,nowdate,nowtime)
    if os.path.isfile(loc):
        os.remove(loc)
    plt.savefig(loc,bbox_inches = 'tight', dpi = 300)
    plt.clf()
    return nowtime #"/static/{1}_{0}_{2}_{3}.png".format(country1,uname,nowdate,nowtime)

#Updates the Curr31 table to contain only the columns of the past 31 days
#Void function, returns None
def updateCurr31():
    lst3 = daysListFromDate(30)
    lst4 = []
    for i in range(len(lst3)):
        undname30 = convertDateToUnderscore(lst3[i])
        lst4.append(undname30)
    cursor.execute("select column_name from information_schema.columns where table_name = 'Curr31'")
    d = cursor.fetchall()
    for i in range(len(d)-1):
        if d[i][0] not in lst4 and d[i][0] != 'CurrCode':
            query = '''ALTER TABLE Curr31
                DROP {0}'''
            cursor.execute(query.format(d[i][0]))
            mycon.commit()
    for i in range(len(lst3)):
        undname31 = convertDateToUnderscore(lst3[i])
        tup = (undname31,)
        if tup not in d:
            url31 = 'http://data.fixer.io/api/'+ lst3[i] +'?access_key=104d12bf481223711dd4e2e0cf6eaac0'
            values31 = convertToUSD(callAPI(url31))
            query = '''ALTER TABLE Curr31
                ADD ({0} float)'''
            cursor.execute(query.format(undname31))
            mycon.commit()
            for key in values31['rates']:
                query1 = '''UPDATE Curr31
                   SET {2} = "{1}"     
                   WHERE CurrCode = "{0}"'''        
                cursor.execute(query1.format(key,values31['rates'][key],undname31))
                mycon.commit()

#Takes in the name, start and end date strings in DD-MM-YYYY format, a csv string of all the countries and also a URL
#Creates a log table, if it doesn't exist already, with the required columns
#Updates the log table, inserting the details regarding the latest usage of the application, does not insert if an error is produced
#Is a void function, returns None
def updateLog(name1,stdate1,endate1,csv1,url1):
    cursor.execute('''create table IF NOT EXISTS 
                   Log(sno integer PRIMARY KEY,name varchar(100) NOT NULL,count integer NOT NULL,
                       logindatetime datetime NOT NULL,startdate date NOT NULL,enddate date NOT NULL,
                       countries varchar(1000) NOT NULL,url varchar(1000) NOT NULL)''')            
    mycon.commit()
    cursor.execute("select count(sno) from Log")
    snocount = cursor.fetchone()
    sno = snocount[0] + 1
    stdate1 = datetime.strptime(stdate1, "%d-%m-%Y").strftime("%Y-%m-%d")
    endate1 = datetime.strptime(endate1, "%d-%m-%Y").strftime("%Y-%m-%d") 
    cursor.execute("SELECT COUNT(sno) FROM Log WHERE name = '{0}'".format(name1))
    namecount = cursor.fetchone()
    count1 = namecount[0] + 1
    logdate1 = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''insert into Log 
                   values("{0}","{1}","{2}","{3}","{4}","{5}","{6}","{7}")'''.format(sno,name1,count1,logdate1,stdate1,endate1,csv1,url1))                
    

updateCurr31()
currcountries()

#Creates list of common countries and colors and selects a random sample of 4 elements from each list
#Saves these 4 graphs, to be displayed on the landing page
uk = "United Kingdom of Great Britain and Northern Ireland"
commonlist = ["India",uk,"Japan","China","France","Switzerland","Singapore","Australia","Canada","Bitcoin","Gold","Silver"]
colorlist = ['blue','red','green','yellow','orange','cyan','purple','magenta','brown','white']
rlist = random.sample(commonlist,4)
slist = random.sample(colorlist,4)
srcode1 = saveGraph(rlist[0],slist[0])
srcode2 = saveGraph(rlist[1],slist[1])
srcode3 = saveGraph(rlist[2],slist[2])
srcode4 = saveGraph(rlist[3],slist[3])

#Opens the HTML file
f = open('test-post-1.html','w+')

#Fetches all the names of the countries in the table currcountries
cursor.execute("select Name from currcountries ")
code = cursor.fetchall()

#HTML code to be shown as the landing page
#Includes a form which will 'POST' the obtained values like name, dates and countries to the Flask application at localhost:5000/login
#Text boxes are created for the dates and name and a multiselect dropdown menu for the countries
message = """<html>
<head>
    <title> CS Project </title>
</head>
<body>	 
	<form action = "http://localhost:5000/login" method = "POST">
        <center><h1>Welcome to our CS Project</h1></center>
		<label for="nm">Enter Name:</label> 
		<input type = "text" name = "nm" id = "nm" /><br><br>
        <label for="date1">Enter Start Date in DD-MM-YYYY format:</label>
        <input type = "text" name = "date1" id = "date1" /><br><br>
        <label for="date2">Enter End Date in DD-MM-YYYY format:</label>
        <input type = "text" name = "date2" id = "date2" /><br><br>
        <label for="currency1">Choose your countries (Press Ctrl to multiselect) : </label>
        <select name="currency1" id="currency1" multiple>"""

#Inserting all the countries into the dropdown menu
for i in range(len(code)):
    message = message + """<option value = "{0}" >{0}</option>""".format(code[i][0])

#Displaying the 4 earlier saved images on the landing page
message = message + """</select>    
		<input type = "submit" value = "submit" />
	</form>
    <img align = "left" src = "file:///C:/Users/Anand/Coding/Images/{0}-{4}-2-sample.png" alt = "Sample image" width = "750" height = "375">
    <img src = "file:///C:/Users/Anand/Coding/Images/{1}-{4}-2-sample.png" alt = "Sample image" width = "750" height = "375">	 
    <img align = "left" src = "file:///C:/Users/Anand/Coding/Images/{2}-{4}-2-sample.png" alt = "Sample image" width = "750" height = "375">
    <img src = "file:///C:/Users/Anand/Coding/Images/{3}-{4}-2-sample.png" alt = "Sample image" width = "750" height = "375">
    
</body>
</html>""".format(rlist[0],rlist[1],rlist[2],rlist[3],date.today())

f.write(message)
f.close()

webbrowser.open_new_tab('test-post-1.html')





from flask import Flask, redirect, url_for, request 
#Constructing a Flask object called app, taking the name of the current module, in this case, '__main__'
app = Flask(__name__) 

#Assigning a URL to the below function with the help of @app.route
#This decorator tells the application to execute the below function when the user visits the particular local URL
@app.route('/success/<name>/<sdate>/<edate>/<curr1>/<count>')

#Takes the name,date strings in DD-MM-YYYY and also the csv string containing the countries selected
#Obtains the last searched URL by the user
#Creates a random sample of colors to fit the no of countries
#Calls the ultimateFunction on the name and the dates
#Displays a HTML message that displays the last URL searched by the user
#For each country, calls the saveDateGraph function to save the particular graphs and finally displays it 
def success(name,sdate,edate,curr1,count):
    count = int(count)
    requrl = "http://localhost:5000/success/{0}/{1}/{2}/{3}/{4}".format(name,sdate,edate,curr1,count)
    cursor.execute("select url from log where name = '{0}'".format(name))
    reqtup = (requrl,)
    histurl1 = cursor.fetchall()
    index1 = count - 1
    curr1 = curr1.split(",")
    colorlst = ['blue','red','green','yellow','cyan','orange','purple','brown','magenta','white','pink','olive','gold']
    n1 = len(colorlst)
    n = len(curr1)
    if n1>=n:
        randcolorlst = random.sample(colorlst,n)
    else:
        randcolorlst = random.sample(colorlst,n1)*(n//n1 + 1)
    ultimateFunction(name, sdate, edate)
    message1 = '''<html>
                  <head>
                      <title> Success!!! </title>
                  </head>
                  <body>
                      <h1><center>Hello {0}</center></h1>'''.format(name)
    if index1>0:
        histurl = histurl1[index1-1][0]
        message1+= '''<h3><center>You have made {1} no of valid searches so far<br><br> <a href="{0}" target = "_blank">Your last search is</a></center></h3>'''.format(histurl,count)
    elif index1 == 0:
        message1+='''<h3><center>This is your first search </center></h3>'''
    #for i in range(n):
        #message1+='''<h3>The value of {1} is {0} <br></h3>'''.format(getCurrCodeLatest(curr1[i]),getCurrCode(curr1[i]))
    for i in range(n):
        rn = randcolorlst[i]
        src1 = saveDateGraph(name, sdate, edate, curr1[i], rn)
        #message1+='''<img src = {0} alt = "Sample image" width = "750" height = "375"/>'''.format(src1)
        message1+='''<img src = "/static/{1}_{0}_{2}_{3}.png" alt = {0} width = "750" height = "375"/>'''.format(curr1[i],name,date.today(),src1)
        #message1+='''<img src = "file:///C:/Users/Anand/Coding/Images/{1}_{0}_{2}.png"  alt = {0} '''.format(curr1[i],name,date.today())
    message1+='''</body>
              </html>'''
    return message1
    
@app.route('/error/<name>')
#Deals with errors produced due to the incorrect date format entered
def error(name):
    cursor.execute("select url from log where name = '{0}'".format(name))
    histurl1 = cursor.fetchall()[-1]
    histurl = histurl1[0]
    message2 = '''<html>
    <head>
    <title> Error!!! </title>
    </head>
    <body>
    <h1><center>Hello {0}<br></center></h1>
    <h3><center><a href="{1}" target = "_blank">Your last search<br></a></center></h3>
    <h2>Sorry {0}, your date values must be typed in DD-MM-YYYY format only'''.format(name,histurl)
    return message2


#Accepts the 'POST' sent by the HTML file and depending on whether an error is produced, redirects you to either the success or the error url
#List values are converted to CSV as list objects are not allowed to be part of the URL
#Also calls updateLog function to update the log if there is no error produced
@app.route('/login',methods = ['POST', 'GET']) 
def login():
    if request.method == 'POST':
        user = request.form.get('nm')
        date1 = request.form.get('date1')
        date2 = request.form.get('date2')
        dt1 = stringToDatetime(date1)
        dt2 = stringToDatetime(date2)
        if dt1>date.today() or dt2>date.today() or dt1>dt2 : 
            return redirect(url_for('error',name = user))
        try:
            cur1 = request.form.getlist('currency1')
            cur1_csv = ",".join(cur1)
            cursor.execute("SELECT COUNT(sno) FROM Log WHERE name = '{0}'".format(user))
            namecount = cursor.fetchone()
            count1 = namecount[0] + 1
            requrl = "http://localhost:5000/success/{0}/{1}/{2}/{3}/{4}".format(user,date1,date2,cur1_csv,count1)
            updateLog(user,date1,date2,cur1_csv,requrl)
            return redirect(url_for('success',name = user,sdate = date1,edate = date2,curr1 = cur1_csv, count = count1))
        except:
            return redirect(url_for('error',name = user)) 

#Checks if __name__ = '__main__' in order to run the application, with debug mode on
if __name__ == '__main__': 
    app.run(debug = True)