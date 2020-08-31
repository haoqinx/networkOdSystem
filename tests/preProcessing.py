import pandas as pd
import numpy as np

indexNum={
    "src_ip":8,
    "dst_ip":10,
    "application_name":92,
    "category_name":93,
    "client_info":94,
    "server_info":95,
    "j3a_client":96,
    "j3a_server":97
}
AVG_VALUE=[]
dropColumn=[]
def display(df):
    print(df.head(5))
    print(df.iloc[0,:])

applist={}

'''将非数值化数据转换成数值化数据,删除后面四列无用数据
   (缺失度太高)，删除时间戳
'''
def changeStr2Vec(df):
    print("changing str2vec")
    for i in range(len(df)):
        #对源ip地址和目的ip地址进行整数转换
        srcIp=df.iloc[i]['src_ip']
        dstIp=df.iloc[i]['dst_ip']

        df.iloc[i,indexNum['src_ip']]=srcIp.replace(".","")
        df.iloc[i,indexNum['dst_ip']]=dstIp.replace(".","")

        #对applicatino_name和category_name字符串进行数值化
        if(df.iloc[i,indexNum['application_name']]=="HTTP"):
            df.iloc[i,indexNum['application_name']] = 1
        else:
            df.iloc[i,indexNum['application_name']] = 0

    df.drop(columns=['id','category_name', 'client_info', 'server_info', 'j3a_client', 'j3a_server',
                         'bidirectional_first_seen_ms', 'bidirectional_last_seen_ms', 'src2dst_first_seen_ms',
                         'src2dst_last_seen_ms', 'dst2src_first_seen_ms', 'dst2src_last_seen_ms'], inplace=True)
#寻找平均值用于填充缺失值
def valueNormalization(df):
    print("valueNormalization")
    AVG_VALUE=[]
    for j in range(len(df.loc[0])):
        value=0
        row_number = len(df)
        for i in range(len(df)):
            if not np.isnan(int(df.loc[i][j])):
                value+=int(df.loc[i][j])
            else:
                row_number-=1
        AVG_VALUE.append(value/row_number)


#使用平均值替换缺失值
def  findMissingValue(df):
    print("findMissingValue")
    missingThreshold=len(df)*0.5
    for j in range(len(df.iloc[0])):
        missValue = 0
        for i in range(len(df)):
            if(np.isnan(int(df.iloc[i][j]))):
                missValue+=1
                df.iloc[i,j]=AVG_VALUE[i]
        if missValue>=missingThreshold:
            dropColumn.append(j)
    for x in dropColumn:
        df.drop(columns=[df.columns.tolist()[x]], inplace=True)




if __name__=="__main__":
    '''
    数据预处理
    '''
    # df=pd.read_csv("target.csv")
    # changeStr2Vec(df)
    # valueNormalization(df)
    # findMissingValue(df)
    # df.to_csv("source.csv")
    df=pd.read_csv("./data/0708103916.csv")
    changeStr2Vec(df)
    # valueNormalization(df)
    # findMissingValue(df)
    df.fillna(df.mean())
    df.to_csv("res.csv")
