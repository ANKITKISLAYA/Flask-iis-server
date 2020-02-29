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
import warnings
warnings.filterwarnings("ignore")

app = flask.Flask(__name__)
app.debug = True

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

@app.route('/bar')
def bar():
    return "The URL for this page is  sfdsf{}".format(url_for('bar'))


@app.route('/test', methods=['GET'])
def home():
    return '''<h1>Distant Reading Archive</h1>
<p>A prototype API for distant reading of science fiction novels.</p>'''

@app.route('/api/books/all', methods=['GET'])
def api_all():
    return jsonify(books)


@app.route('/api/books', methods=['GET'])
def api_id():
    # Check if an ID was provided as part of the URL.
    # If ID is provided, assign it to a variable.
    # If no ID is provided, display an error in the browser.
    if 'id' in request.args:
        id = int(request.args['id'])
    else:
        return "Error: No id field provided. Please specify an id."

    # Create an empty list for our results
    results = []

    # Loop through the data and match results that fit the requested ID.
    # IDs are unique, but other fields might return many results
    for book in books:
        if book['id'] == id:
            results.append(book)

    # Use the jsonify function from Flask to convert our list of
    # Python dictionaries to the JSON format.
    return jsonify(results)

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
    # item_ware=[itemname,warehouseid]

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
        my_list =[rows.itemname, rows.ItemId]
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
            my_list =[rows.itemname,rows.CategoryName]
            Row_list.append(my_list)
        choices = Row_list
        t=process.extract(itemname, choices, limit=10)

        l1=list()
        for j in range(len(t)):
            if (t[j][1]>50):
                a=(t[j][0])
                l1.append(a)

        item1=list()
        if len(l1)>=1:
            for i in l1:
                a=(i[0])
                item1.append(a)
        item=item1
        m=len(item1)

    # if m>=2:
    #     Row_list =[]
    #     l='please check your spell and try again'
    #     for index, rows in df.iterrows():
    #         my_list =[rows.itemname,rows.SubsubcategoryName]
    #         Row_list.append(my_list)
    #     choices = Row_list
    #     t=process.extract(itemname, choices, limit=10)
    #
    #     l2=list()
    #     for j in range(len(t)):
    #         if (t[j][1]>50):
    #             a=(t[j][0])
    #             l2.append(a)
    #
    #     item2=list()
    #     if len(l2)>=1:
    #         for i in l2:
    #             a=(i[0])
    #             item2.append(a)
    #     a=len(item2)
    #     item=item2
    item_set=[parle,maggi,vim,tasty-hasty,ata,kisan kirana,rice]
    # if len(item)>5:
    #     return jsonify(item)
    # else:
    return jsonify(item_set)


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

    return "The URL for this page is  sfdsf{}".format(url_for('read'))





if __name__ == '__main__':
    app.run(host='0.0.0.0',port=9010)
