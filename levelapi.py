# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 10:54:46 2019

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
import numpy as np



from aes256 import aes256



class levelapi:
    
    def api(self,month,year,level):

        month = int(month)
        year = int(year)
        level = int(level)
        
        #url = "https://shopkirana.in/api/Customers/GetCustDetailLabel?month=%s&year=%s" % (month,year)
        url = "https://er15.xyz:4436/api/Customers/CRMLevelCustomerDetail?month=%s&year=%s" % (month,year)
        #url = "https://shopkirana.in/api/Customers/GetCustDetailLabel?month=10&year=2019" 
        
        resp = requests.get(url)
        json_data = resp.json()
        
        
        if(json_data['Status'] =="OK"):
            redisAesKey = datetime.today().strftime('%Y%m%d') + "1201"
            jso = aes256().decrypt(json_data["Data"],redisAesKey)
            js = json.loads(jso)
            df = json_normalize(js)
           # df=df.loc[df['IsActive'] == True]
            
        df.loc[df.Volume == 0, 'levels'] = 'level_0'
        df.loc[(df.Volume >= 1) , 'levels'] = 'level_1'
        df.loc[(df.Volume >= 10000) & (df.OrderCount >= 3) & (df.BrandCount  >= 5), 'levels'] = 'level_2'
        df.loc[(df.Volume >= 20000) & (df.OrderCount >= 5) & (df.BrandCount  >= 10) & (df.kkVolumn >= 2000), 'levels'] = 'level_3'
        df.loc[(df.Volume >= 30000) & (df.OrderCount >= 8) & (df.BrandCount  >= 20) & (df.kkVolumn >= 8000) & ((df.Selfordercount/(df.OrderCount))*100 > 30), 'levels'] = 'level_4'
        df.loc[(df.Volume >= 75000) & (df.OrderCount >= 12) & (df.BrandCount >= 40) & (df.kkVolumn >= 15000) & ((df.Selfordercount/(df.OrderCount))*100 > 60), 'levels'] = 'level_5'
        
        dfL0 = df.loc[df.levels == 'level_0']
        dfL1 = df.loc[df.levels == 'level_1'] 
        dfL2 = df.loc[df.levels == 'level_2']
        dfL3 = df.loc[df.levels == 'level_3']
        dfL4 = df.loc[df.levels == 'level_4']
        dfL5 = df.loc[df.levels == 'level_5']


        if (level == 0):
            dfL0 = dfL0.to_dict('records')
            return dfL0
        
        elif (level == 1):
            dfL1 = dfL1.to_dict('records')
            return dfL1
        
        elif (level == 2):
            dfL2 = dfL2.to_dict('records')
            return dfL2
            
        elif (level == 3):
            dfL3 = dfL3.to_dict('records')
            return dfL3


        elif (level == 4):
            dfL4 = dfL4.to_dict('records')
            return dfL4

        elif (level == 5):
            dfL5 = dfL5.to_dict('records')
            return dfL5





