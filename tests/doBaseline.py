import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import os

attrlist=[
        "bidirectional_duration_ms",
        "bidirectional_ip_bytes",
        "bidirectional_max_piat_ms",
        "bidirectional_mean_piat_ms",
        "bidirectional_min_piat_ms",
        "bidirectional_packets",
        "bidirectional_raw_bytes",
        "bidirectional_stdev_piat_ms",
        "dst2src_ack_packets",
        "dst2src_duration_ms",
        "dst2src_ip_bytes",
        "dst2src_max_piat_ms",
        "dst2src_mean_piat_ms",
        "dst2src_packets",
        "dst2src_raw_bytes",
        "src2dst_ack_packets",
        "src2dst_duration_ms",
        "src2dst_ip_bytes",
        "src2dst_max_piat_ms",
        "src2dst_mean_piat_ms",
        "dst2src_min_raw_ps",
        "src2dst_raw_bytes",
        "src2dst_stdev_piat_ms"
]



def parseJSON(attr):
    with open("./jsondata/" + attr + ".json")as f:
        classifyKey = []
        data=json.load(f)
        for key in data.keys():
            try:
                # print(data[key][0].split("-")[1].split(".")[0])
                classifyKey.append(key)
            except:
                pass
        return classifyKey
def dataMinus(currentTime , nextTime):
    mounth1=int(currentTime[0:2])
    mounth2=int(nextTime[0:2])

    date1=int(currentTime[2:4])
    date2=int(nextTime[2:4])

    hours1=int(currentTime[4:6])
    hours2=int(nextTime[4:6])

    minute1=int(currentTime[6:8])
    minute2=int(nextTime[6:8])

    seconds1=int(currentTime[8:10])
    seconds2=int(nextTime[8:10])

    res=0

    if seconds2<seconds1:
        minute2-=1
        seconds2+=60
    res+=(seconds2-seconds1)
    if minute2<minute1:
        hours2-=1
        minute2+=60
    res+=(minute2-minute1)*60
    if hours2<hours1:
        date2-=1
        hours2+=24
    res+=(hours2-hours1)*3600

    if date2<date1:
        mounth2-=1
        date2+=31
    res+=(date2-date1)*3600*24

    res+=(mounth2-mounth1)*3600*24*60

    res/=60

    return res



'''
   attr是分类的属性名称
   indexofJsonData是每类的属性下标
   indexOfAimAttr是指标的下标
   score是百分位数
   ck是每类的属性
   '''
def getPercent(attr,indexofJsonData,indexOfAimAttr,score,ck,ck1,addtationattr,additionIndexofJsonData):

    x = [0]
    y = [0]
    currentTime="0708103916"
    filelist=[]
    for file in os.listdir("./"):
        filelist.append(file)
        #print(file)
    filelist.sort(key=lambda x:int(x[0:10]))
    for file in filelist:
        nextTime=file[0:-4]
        df = pd.read_csv(file)
        x.append(x[-1]+dataMinus(currentTime=currentTime,nextTime=nextTime))
        print(x[-1])
        currentTime=nextTime

        serice=df[(df[attr] == ck[indexofJsonData])
                  & (df[addtationattr] == int(ck1[additionIndexofJsonData]))][attrlist[indexOfAimAttr]]

        sortedData=serice.quantile([score])
        serice2int=int(list(sortedData)[0])
        y.append(serice2int)

    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    plt.plot(x, y,label=ck[indexofJsonData])

if __name__=="__main__":
    # with open("./jsondata/app_protocol.json")as f:
    #     parseJSON(f)
    #
    #     pass
    # os.chdir("./data/mycsv")
    # for file in os.listdir("./"):
    #     if file is not "res.csv":
    #         df=pd.read_csv(file)
    #         print(len(df))
    #         df.to_csv("res.csv",header=False,mode="a+",index=False)
    attr = "category_name"
    attr1 = "vlan_id"
    indexOfAimAttr=0
    score=0.9
    ck = parseJSON(attr)
    ck1 = parseJSON(attr1)
    os.chdir("./data/mycsv")
    for i in range(1,len(ck)):
        plt.cla()
        for j in range(1,len(ck1)):
            # print(i)
            try:
                getPercent(attr,i,indexOfAimAttr,score,ck,ck1,attr1,j)
            except:
               print("error")
        plt.legend(loc='upper right')
        plt.title("differentVlanId"+attrlist[indexOfAimAttr]+" in "+str(ck[i])+" of "+str(score*100)+"%")
        plt.savefig("../"+attr+str(indexOfAimAttr)+str(score)+".jpg")



