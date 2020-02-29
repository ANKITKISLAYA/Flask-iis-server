# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 18:54:34 2019

@author: Ankit
"""


import json
import requests
import urllib.parse 
from pandas.io.json import json_normalize
import pandas as pd
import numpy as np
import copy
from datetime import datetime

from flask import Flask , jsonify
from flask import url_for
from aes256 import aes256
from flask import request
from flask_cors import CORS #to remove cross origin issue

from flask_jsonpify import jsonpify

from Target import Target
from Targetvalue import Targetvalue

rough = Flask(__name__)
CORS(rough)    # to remove Error:- No 'Access-Control-Allow-Origin' header is present on the requested resource



# http://111.118.252.170:8181/api/Customers/GetCustDetailLabel?month=4&year=2019  # Data Api


#http://127.0.0.1:5000/allocation?month=5&year=2019&band=3&amount=100000&l0amount=10000&levels=4&cityid=1&warehouseid=7  # Function Api

@rough.route('/target/percent')
def target():
    
    percentage = request.args['percentage']
    levels = request.args['levels']
    ulimit = request.args['ulimit']
    llimit = request.args['llimit']
    #band = request.args['band']
    jso=Target().ret(percentage,levels,ulimit,llimit)
    #JSONP_data = jsonpify(jso)
    return jsonify(jso)
    
@rough.route('/target/value')
def targetvalue():
    
    value = request.args['value']
    levels = request.args['levels']
    ulimit = request.args['ulimit']
    llimit = request.args['llimit']
    #band = request.args['band']  

    jso=Targetvalue().ret(value,levels,ulimit,llimit)
    #JSONP_data = jsonpify(jso)
    return jsonify(jso)
    


if __name__ == '__main__':
    rough.run()
#    rough.run(ssl_context='adhoc') 









