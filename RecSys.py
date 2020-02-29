# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 11:30:37 2020

@author: Ankit
"""

import pandas as pd
from pymongo import MongoClient 
from collections import defaultdict
from operator import itemgetter 


class RecSys:
    
    def rec(self,itemid,number):
        
        citem = int(itemid)
        number = int(number)
        l=[]
        l1=[]
        conn = MongoClient('192.168.1.101', 27017)
        mydb = conn.ankit_database
        collection = mydb.RecSysItem
                
        df1 = pd.DataFrame(list(collection.find( { 'itemid' :1 })))
        df2 = df1.drop(['_id' , 'itemid'], axis = 1)
        df3 = df2.sort_values(0, axis=1, ascending=False, inplace=False, kind='quicksort', na_position='last')
        l1 = list(df3.columns.values)
        
        #lcolumn = list(df1.columns.values)
        #lcolumn = lcolumn[:-2]
        #lcolumn = lcolumn[2:]
        l1 = [int(i) for i in l1]
        
        
        
        
        if (citem in l1):  
            df = pd.DataFrame(list(collection.find( { 'itemid' : citem })))
            df1 = df.drop(['_id' , 'itemid'], axis = 1)
            lcolumn = list(df1.columns.values)
            lcolumn = [int(i) for i in lcolumn]
            lvalue = list(df1.iloc[0])
            mapped = zip(lcolumn , lvalue)
            lis = list(mapped)
            candidates = defaultdict(float)

            for itemid, score in lis:
                candidates[itemid] = score
            
            pos = 0
            for itemID, ratingSum in sorted(candidates.items(), key=itemgetter(1), reverse=True):
                if (itemID != citem ):
                    l.append(itemID)
                    pos += 1
                    if (pos > number-1):
                        break
                    #l = [int(i) for i in l]  
            return tuple(l)
        
        else:
            l = l1[:number]
            return tuple(l)





