import pandas as pd
import numpy as np
import os
from pandas import Series
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

def merging(s1,s2):
    for key in s2.keys():
        print(key,type(key))
        if key in s1.keys():
            s1[key]+=s2[key]
        else:
            s1[key]=s2[key]

def moveAverage():
    pass

def baseline():
    csvdir="./data/testcsv/"

    dstdir="./newdata/"
    dist1="category_name"
    dist2="vlan_id"
    windowSize=5

    set_of_caregory_name=pd.Series()
    set_of_vlan_id=pd.Series()

    for file in os.listdir(csvdir):
        df=pd.read_csv(csvdir+file,dtype={"vlan_id":str})
        s=df[dist1].value_counts()
        merging(set_of_caregory_name,s)

        s=df[dist2].value_counts()

        merging(set_of_vlan_id,s)



    df = pd.read_csv(csvdir+"0708103916.csv")
    for key1 in set_of_caregory_name.keys():
        for key2 in set_of_vlan_id.keys():
            df2 = pd.DataFrame(columns=list(df.columns))
            for file in os.listdir(csvdir):
                df = pd.read_csv(csvdir + file)
                df = df[(df[dist1] == key1) & (df[dist2]== int(key2))]
                print(key1,key2,"长度:",len(df))
                df2=df2.append(df)
            print(len(df2))
            if len(df2)>0:
                print("存在")
                df2.sort_values("bidirectional_first_seen_ms")
                new_df=pd.DataFrame()
                new_df["bidirectional_first_seen_ms"]=df2["bidirectional_first_seen_ms"]
                for attr in attrlist:
                    res=df2.loc[:,attr].rolling(window=windowSize,center=True).mean()
                    new_df[attr+"-"+str(windowSize)+"-mean"]=res
                new_df.to_csv("./newdata/"+str(key1)+"-"+str(key2)+"-"+str(windowSize)+".csv")
            else:
                print("不存在")













