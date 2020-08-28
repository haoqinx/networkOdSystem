from redis import Redis
import struct
import numpy as np
import json
class DataPretreatment():
    def __init__(self,pool,attrlist):
        self.attrlist=attrlist
        self.r = Redis(connection_pool=pool)


    def merging(sef,s1, s2):
        for key in s2.keys():
            # print(key,type(key))
            if key in s1.keys():
                s1[key] += s2[key]
            else:
                s1[key] = s2[key]
    def putData(self,app,data):
        data=str(data)
        return self.r.lpush(str(app),data)


    def getData(self,app):
        # encoded = self.r.lrange(str(app)+"-matrix",0,-1)
        # res=[]
        # for item in encoded:
        #     h, w = struct.unpack('>II', item[:8])
        #     vector = np.frombuffer(encoded[8:]).reshape(h, w)
        #     res.append(vector)
        # res=np.asarray(res,dtype='float32')
        res=[]
        data=self.r.lrange(str(app),0,-1)
        for item in data:
            temp=[]
            record = json.loads(item)
            for attr in self.attrlist:
                temp.append(record[attr])
            temp=np.asarray(temp,dtype=np.float32)
            res.append(temp)
        res=np.asarray(res,dtype=np.float32)
        return res


    def deleteData(self,app):
        self.r.ltrim(str(app),1,0)