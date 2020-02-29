import flask
from flask import request, jsonify, url_for
import json
import requests
import urllib.parse
from pandas.io.json import json_normalize
import pandas as pd
import numpy as np
import copy
from datetime import datetime

#from flask_jsonpify import jsonpify



import sys
import base64
from hashlib import md5
from Crypto import Random
from Crypto.Cipher import AES
from aes256 import aes256
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import pandas as pd
from flask import Response
import json
from collections import Counter
import warnings
warnings.filterwarnings("ignore")


from Target import Target
from Targetvalue import Targetvalue
from levelapi import levelapi
from RecSys import RecSys
from RecSys1 import RecSys1
from RecSys2 import RecSys2
from RecSys2 import RecSys2
from RecSys3 import RecSys3

# from InsertRecSys import InsertRecSys



import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

app = flask.Flask(__name__)
app.debug = True


sentry_sdk.init(
    dsn="https://d4f55392a9aa4f78a816e498c88fb5c3@sentry.io/1873356",
    integrations=[FlaskIntegration()]
)




# Create some test data for our catalog in the form of a list of dictionaries.
books = [
    {'id': 0,
     'title': 'A Fire Upon the Deep',
     'author': 'Vernor Vinge',
     'first_sentence': 'The coldsleep itself was dreamless.',
     'year_published': '1992'},
    {'id': 1,
     'title': 'The Ones Who Walk Away From Omelas',
     'author': 'Ursula K. Le Guin',
     'first_sentence': 'With a clamor of bells that set the swallows soaring, the Festival of Summer came to the city Omelas, bright-towered by the sea.',
     'published': '1973'},
    {'id': 2,
     'title': 'Dhalgren',
     'author': 'Samuel R. Delany',
     'first_sentence': 'to wound the autumnal city.',
     'published': '1975'}
]


class PrefixMiddleware(object):
#class for URL sorting
    def __init__(self, app, prefix=''):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        #in this line I'm doing a replace of the word flaskredirect which is my app name in IIS to ensure proper URL redirect
        if environ['PATH_INFO'].lower().replace('/flaskredirect','').startswith(self.prefix):
            environ['PATH_INFO'] = environ['PATH_INFO'].lower().replace('/flaskredirect','')[len(self.prefix):]
            environ['SCRIPT_NAME'] = self.prefix
            return self.app(environ, start_response)
        else:
            start_response('404', [('Content-Type', 'text/plain')])
            return ["This url does not belong to the app.".encode()]


app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix='/foo')


@app.route('/api/search', methods=['GET'])
def api_name():
    # Check if an ID was provided as part of the URL.
    # If ID is provided, assign it to a variable.
    # If no ID is provided, display an error in the browser.
    if 'itemname' in request.args:
        itemname = request.args['itemname']
    else:
        return "Error: No id field provided. Please specify an itemname."

    if 'warehouseid' in request.args:
        warehouseid = int(request.args['warehouseid'])
    else:
        return "Error: No id field provided. Please specify an warehouseid."

    url = "https://uat.shopkirana.in/api/itemMaster/Getitemmasterscentral"
    resp = requests.get(url)
    json_data = resp.json()

    if(json_data["Status"] =="OK"):
        redisAesKey = datetime.today().strftime('%Y%m%d') + "1201"
        jso = aes256().decrypt(json_data["Data"],redisAesKey)
        js = json.loads(jso)
        df = json_normalize(js)

    df=df[df.WarehouseId==warehouseid]
    df=df[['itemname', 'ItemId','CategoryName','SubsubcategoryName','WarehouseId']]

    p= df.groupby('itemname').max()

    df=p.reset_index()


    Row_list =[]
    for index, rows in df.iterrows():
        my_list =[rows.ItemId, rows.itemname]
        Row_list.append(my_list)
    choices = Row_list
    t=process.extract(itemname, choices, limit=10)

    l=list()

    for j in range(len(t)):
        if (t[j][1]>50):
            a=(t[j][0])
            l.append(a)

    item=list()
    if len(l)>=1:
        for i in l:
            a=(i[0])
            item.append(a)
    l=len(item)

    if l<=2:
        Row_list =[]
        for index, rows in df.iterrows():
            my_list =[rows.itemname,rows.CategoryName, rows.ItemId]
            Row_list.append(my_list)
        choices = Row_list
        t=process.extract(itemname, choices, limit=10)

        l1=list()
        for j in range(len(t)):
            if (t[j][1]>75):
                a=(t[j][0])
                l1.append(a)

        item1=list()
        if len(l1)>=1:
            for i in l1:
                a=(i[2])
                item1.append(a)
        item=item1
        m=len(item1)

    if l<2  and m<2:
        Row_list2 =[]
        # l='please check your spell and try again'
        for index, rows in df.iterrows():
            my_list =[rows.itemname,rows.SubsubcategoryName, rows.ItemId]
            Row_list2.append(my_list)
        choices = Row_list2
        t=process.extract(itemname, choices, limit=10)

        l2=list()
        for j in range(len(t)):
            if (t[j][1]>75):
                a=(t[j][0])
                l2.append(a)

        item2=list()
        if len(l2)>=1:
            for i in l2:
                a=(i[2])
                item2.append(a)
        a=len(item2)
        item=item2
    # item_set=(parle,maggi,vim,tasty-hasty,ata,kisan kirana,rice)
    # # l=json.dumps(l)
    if len(item)<5:
        return Response(None)
    else:
        return jsonify(item)

@app.route('/read/data', methods=['GET'])
def read():
    url = "https://uat.shopkirana.in/api/itemMaster/Getitemmasterscentral"
    resp = requests.get(url)
    json_data = resp.json()

    if(json_data["Status"] =="OK"):
        redisAesKey = datetime.today().strftime('%Y%m%d') + "1201"
        jso = aes256().decrypt(json_data["Data"],redisAesKey)
        js = json.loads(jso)
        df = json_normalize(js)

    return jsonify(js)

@app.route('/read/new', methods=['GET'])
def item(id):
    df = pd.read_excel('\\192.168.1.101\\PyhtonAPIs\\data.xlsx')

    dataset=list(df.groupby('OrderId')['ItemId'].apply(list))

    id=int(input())
    lst=list()
    for i in range(len(dataset)):
        for j in dataset[i]:
            if j==id:

                lst.append(i)

    l=list()
    for i in lst:
        l.append(dataset[i])

    flat_list = [item for sublist in l for item in sublist]

    most_occur = Counter(flat_list).most_common(6)

    lst=list()
    for i in  most_occur:
        lst.append(i[0])

    # lst.remove(id)

    return jsonify(df)
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
@app.route('/allocation')
def allocation():

    month = request.args['month']
    year = request.args['year']
    band = request.args['band']
    amount = request.args['amount']
    l0amount = request.args['l0amount']
    levels = request.args['levels']
    cityid = request.args['cityid']
    warehouseid = request.args['warehouseid']

    l0amount = int (l0amount)
    band = int (band)
    amount = int (amount)
    level = int (levels)
    warehouseid = int(warehouseid)
    cityid = int(cityid)


## getting data:- reading data from the api in json format and converting it into python dataframe using json_normalize


    # url = "http://111.118.252.170:8181/api/Customers/GetCustDetailLabel?month=%s&year=%s" % (month, year)
    # url = "http://192.168.1.113/api/Customers/GetCustDetailLabel?month=%s&year=%s" % (month, year)

    url = "https://uat.shopkirana.in/api/Customers/GetCustDetailLabel?month=%s&year=%s" % (month,year)
    resp = requests.get(url)
    json_data = resp.json()


    if(json_data['Status'] =="OK"):
        redisAesKey = datetime.today().strftime('%Y%m%d') + "1201"
        jso = aes256().decrypt(json_data["Data"],redisAesKey)
        js = json.loads(jso)
        df = json_normalize(js)
        df=df.loc[df['IsActive'] == True]


##  levelling :- segregating the customers into levels using definition below and storing each level into the list

    df.loc[df.Volume == 0, 'levels'] = 'level_0'
    df.loc[df.Volume >= 1, 'levels'] = 'level_1'
    df.loc[(df.Volume >= 10000) & (df.OrderCount >= 3) & (df.BrandCount  >= 5), 'levels'] = 'level_2'
    df.loc[(df.Volume >= 20000) & (df.OrderCount >= 5) & (df.BrandCount  >= 10) & (df.kkVolumn >= 2000), 'levels'] = 'level_3'
    df.loc[(df.Volume >= 30000) & (df.OrderCount >= 8) & (df.BrandCount  >= 20) & (df.kkVolumn >= 8000) & ((df.Selfordercount/(df.Salespersonordercount+df.Selfordercount))*100 > 30), 'levels'] = 'level_4'
    df.loc[(df.Volume >= 75000) & (df.OrderCount >= 12) & (df.BrandCount >= 40) & (df.kkVolumn >= 15000) & ((df.Selfordercount/(df.Salespersonordercount+df.Selfordercount))*100 > 60), 'levels'] = 'level_5'
    
    dfL0 = df.loc[df.levels == 'level_0']
    dfL1 = df.loc[df.levels == 'level_1'] 
    dfL2 = df.loc[df.levels == 'level_2']
    dfL3 = df.loc[df.levels == 'level_3']
    dfL4 = df.loc[df.levels == 'level_4']
    dfL5 = df.loc[df.levels == 'level_5']
    
    l = (dfL0 , dfL1 , dfL2 , dfL3 , dfL4 ,dfL5)



## Status :- based on the bands giving status to the skcode (promotion , retention , consistent) . bands are based on percentile . 
# for example : - in band1 above 90 percentile is promotion and below 10% is retention and between 90 - 10 percentile is consistent 

    b = band
    l = list(l) 
    i = level
    df1 = copy.deepcopy(l[i])

    if (b == 1):
            
            df1.loc[(df1.Volume >= df1.Volume.quantile(0.9)) , 'status'] = 'Promotion'   #  Above 90 percentile Promotion              
            df1.loc[(df1.Volume <= df1.Volume.quantile(0.1)) , 'status'] = 'Retention'   #  Below 10 percentile Retention
            df1.loc[(df1.Volume > df1.Volume.quantile(0.1)) & (df1.Volume < df1.Volume.quantile(0.9)), 'status'] = 'Consistent' # between 90 and 10 percentile is consistent
            
     
    elif (b == 2):
              
            df1.loc[(df1.Volume >= df1.Volume.quantile(0.8)) , 'status'] = 'Promotion'   #  Above 80 percentile Promotion
            df1.loc[(df1.Volume <= df1.Volume.quantile(0.2)) , 'status'] = 'Retention'   #  Below 20 percentile Retention  
            df1.loc[(df1.Volume > df1.Volume.quantile(0.2)) & (df1.Volume < df1.Volume.quantile(0.8)), 'status'] = 'Consistent' # between 80 and 20 percentile is consistent

        
        
    elif (b == 3):
         
            df1.loc[(df1.Volume >= df1.Volume.quantile(0.7)) , 'status'] = 'Promotion'    #  Above 70 percentile Promotion
            df1.loc[(df1.Volume <= df1.Volume.quantile(0.3)) , 'status'] = 'Retention'    #  Below 30 percentile Retention
            df1.loc[(df1.Volume > df1.Volume.quantile(0.3)) & (df1.Volume < df1.Volume.quantile(0.7)), 'status'] = 'Consistent'  # between 70 and 30 percentile is consistent

  
        
            
    elif(b == 4):
   
            df1.loc[(df1.Volume >= df1.Volume.quantile(0.6)) , 'status'] = 'Promotion'     #  Above 60 percentile Promotion
            df1.loc[(df1.Volume <= df1.Volume.quantile(0.4)) , 'status'] = 'Retention'     #  Above 40 percentile Promotion
            df1.loc[(df1.Volume > df1.Volume.quantile(0.4)) & (df1.Volume < df1.Volume.quantile(0.6)), 'status'] = 'Consistent'  # between 60 and 40 percentile is consistent

   



##  allocation :-  allocating the amount based on the proportion of share in total volume during the month


    Total = 0
    
    for i in range(0,6): 
    
        Total = Total + l[i]['Volume'].sum()

           
    if (level != 0):
        l_amount = (df1['Volume'].sum() / Total) * amount      # each level will be allocated based on the proportion of share in total volume
        pro_c=df1.loc[df1.status == 'Promotion']['SkCode'].count()
        ret_c=df1.loc[df1.status == 'Retention']['SkCode'].count()

        
        pro_am = l_amount / 2                            # promotion amount and retention amount will be 50% i.e half of total volume 
        
        
        if ((pro_c != 0) & (ret_c != 0)):
            pro_all=int(pro_am / pro_c)                    #promotion amount will be distributed equally among  promotion customers similar is case with retention customers
            ret_all=int(pro_am / ret_c)
            
        else :
            pro_all = 0
            ret_all = 0
                       
        
        df1.loc[df1.status == 'Promotion', 'allocation'] = str(pro_all)
        df1.loc[df1.status == 'Retention', 'allocation'] = str(ret_all)
        df1.loc[df1.status == 'Consistent', 'allocation'] = str(0)


    else:
        pro_c0 = df['SkCode'].count()                                 # for level0 (l0) there will be seperate allocation and it will be allocated equally among customers
        l0_all = l0amount/pro_c0
        df1.loc[df1.status == 'Promotion', 'allocation'] = str(l0_all)
        df1.loc[df1.status == 'Retention', 'allocation'] = str(l0_all)
        df1.loc[df1.status == 'Consistent', 'allocation'] = str(l0_all)

    
    




        
    df1 = df1.loc[(df1.Cityid == cityid) & (df1.WarehouseId == warehouseid)]
    df1= df1.to_json(orient='records')
    return df1 

	
	
	
	
	
	
@app.route('/target/percent')
def target():
    
    percentage = request.args['percentage']
    levels = request.args['levels']
    ulimit = request.args['ulimit']
    llimit = request.args['llimit']
    #band = request.args['band']

    
    jso=Target().ret(percentage,levels,ulimit,llimit)
    #JSONP_data = jsonpify(jso)
    return jsonify(jso)
    
@app.route('/target/value')
def targetvalue():
    
    value = request.args['value']
    levels = request.args['levels']
    ulimit = request.args['ulimit']
    llimit = request.args['llimit']
    #band = request.args['band']

    jso=Targetvalue().ret(value,levels,ulimit,llimit)
    #JSONP_data = jsonpify(jso)
    return jsonify(jso)
	


@app.route('/levelling')
def levelling():
    
    month = request.args['month']
    year = request.args['year']
    level = request.args['level']
    
    jso=levelapi().api(month,year,level)
    return jsonify(jso)
	


@app.route('/recsysitem')
def recsysitem():
    
    itemid = request.args['itemid']
    number = request.args['number']
    
    jso=RecSys().rec(itemid,number)
    return jsonify(jso)
	


@app.route('/recsysitem1')
def recsysitem1():
    
    itemid = request.args['itemid']
    number = request.args['number']
    wid = request.args['warehouseid']
    jso=RecSys1().rec(itemid,number,wid)
    return jsonify(jso)

@app.route('/recsysitem2')
def recsysitem2():
    
    itemid = request.args['itemid']
    number = request.args['number']
    wid = request.args['warehouseid']
    jso=RecSys2().rec(itemid,number,wid)
    return jsonify(jso)


@app.route('/recsysitem3')
def recsysitem3():
    
    itemid1 = request.args['itemid1']
    itemid2 = request.args['itemid2']
    itemid3 = request.args['itemid3']
    itemid4 = request.args['itemid4']
    itemid5 = request.args['itemid5']
    
    number = request.args['number']
    wid = request.args['warehouseid']
    jso=RecSys3().rec(itemid1,itemid2,itemid3,itemid4,itemid5,number,wid)
    return jsonify(jso)



@app.route('/insertmatrix')
def insertmatrix():
    
    df1 = InsertRecSys().read()
    df2 = InsertRecSys().ExtractItemid(df1)
    df3 = InsertRecSys().Clean(df2)
    df4 = InsertRecSys().AddRating(df3)
    df5 = InsertRecSys().RenameColumns(df4)
    ltup = InsertRecSys().CosineSimilarityMatrix(df5)
    finalfreq = InsertRecSys().finalfreq(ltup)

    SimMat = ltup[0]
    lv = list(finalfreq.values())
    lc = list(finalfreq.keys())
    SimMat1 = lv * SimMat
    df_final = pd.DataFrame(SimMat1, columns = lc , index = lc)
    df_columns = df_final.columns.astype(str)
    lcolumn = list(df_columns)
    df1 = pd.DataFrame(df_final.values , columns = lcolumn , index = lcolumn)
    df1.reset_index(inplace=True,drop = True)
    lcolumn = [int(i) for i in lcolumn]
    df1.insert(0,"itemid",lcolumn)
    
    InsertRecSys().insertdata(df1)
    
    return ("Data Inserted")





@app.route('/getmongodata')
def getmongodata():
    
    js = ApiGetMongo().read()
    
    
    return (js)
    
    


if __name__ == '__main__':
    app.run()
