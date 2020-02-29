# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 16:35:46 2019

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

#from flask import Flask , jsonify


from aes256 import aes256

#muffview

    
class Target:
    
    def ret(self , perc,level,ulimit,llimit):
        
        perc = int (perc)
        level = int (level)
        ulimit = float(ulimit)
        llimit = float(llimit)
        #band = int(band)
        
        #url = "https://er15.xyz:4436/api/Customers/GetCustDetailLabel?month=10&year=2019"
        url = "https://er15.xyz:4436/api/Customers/CRMLevelCustomerDetail?month=12&year=2019"
        
        resp = requests.get(url)
        json_data = resp.json()
        
        if(json_data['Status'] =='OK'):
            redisAesKey = datetime.today().strftime('%Y%m%d') + "1201"
            jso = aes256().decrypt(json_data['Data'],redisAesKey)
            js = json.loads(jso)
            df = json_normalize(js)
            #df = df.loc[df['IsActive'] == True]
        
        # #json_data = requests.get(url).json()
        # json_data = resp.json()
        # df=json_normalize(json_data)
        
        
        #ACTIVE = df[(df.IsActive == True)]
        #INACTIVE = df[(df.IsActive == False)]
        #df=ACTIVE
        #print(df.head(2))
        df['SelfOrderPercentage']=((df['Selfordercount'])/(df['Selfordercount']+df['Salespersonordercount'])*100)
        df['SalesOrderPercentage']=(df['Salespersonordercount'])/(df['Selfordercount']+df['Salespersonordercount'])*100
        df.fillna(0)
        df = df.replace(np.NaN,0)
        df.rename(columns = {"kkVolumn":"KKvolume"},inplace = True)
        
        ######  LEVEL DEFINITIONS BEING DEFINED
        df.loc[df.Volume == 0, 'levels'] = 'Level 0'
        df.loc[df.Volume >= 1, 'levels'] = 'Level 1'
        df.loc[(df.Volume >= 10000) & (df.OrderCount >= 3) & (df.BrandCount  >= 5), 'levels'] = 'Level 2'
        df.loc[(df.Volume >= 20000) & (df.OrderCount >= 5) & (df.BrandCount  >= 10) & (df.KKvolume >= 2000), 'levels'] = 'Level 3'
        df.loc[(df.Volume >= 30000) & (df.OrderCount >= 8) & (df.BrandCount  >= 20) & (df.KKvolume >= 8000) & ((df.Selfordercount/(df.Salespersonordercount+df.Selfordercount))*100 > 30), 'levels'] = 'Level 4'
        df.loc[(df.Volume >= 75000) & (df.OrderCount >= 12) & (df.BrandCount >= 40) & (df.KKvolume >= 15000) & ((df.Selfordercount/(df.Salespersonordercount+df.Selfordercount))*100 > 60), 'levels'] = 'Level 5'
        df.round(2)
        #
        l0=df[df['levels'] == 'Level 0']
        l1=df[df['levels'] == 'Level 1']
        l2=df[df['levels'] == 'Level 2']
        l3=df[df['levels'] == 'Level 3']
        l4=df[df['levels'] == 'Level 4']
        l5=df[df['levels'] == 'Level 5']
        
        
        
        l=[l0,l1,l2,l3,l4,l5]
        
 
    
        
        
        
        perc1 = perc/100
        i=level
        
        if ( perc == 0):
            l[i]['Target'] = 0
            
        # elif (value != 0 & percentage == 0):
        #     l[i]['Target'] = [(int(j) + value) for j in l[i]['Volume']]
            
        else:
        
             l[i]['Target'] = [((int(j) * perc1)+int(j)) for j in l[i]['Volume']]
             
             
        l[i].sort_values(by='Volume', ascending=False)
        df1 = l[i][['SkCode','Cityid','WarehouseName','WarehouseId','levels','Volume','Target']]
        df1 = df1[(df1['Volume'] < ulimit) & (df1['Volume'] >= llimit) ]
        #df1['Band'] = band
        df1 = df1.sort_values(by='Volume', ascending=False)
        #df_list = df1.values.tolist()
        #df1 = df1.to_json(orient='records')
        df1 = df1.to_dict('records')
        return df1
    
        





















