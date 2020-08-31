import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import json
import glob


names=['master_protocol','app_protocol','application_name','category_name','client_info','server_info','src_ip','dst_ip',
       'src_port','dst_port','vlan_id']

times=['bidirectional_first_seen_ms','bidirectional_last_seen_ms','src2dst_first_seen_ms','src2dst_last_seen_ms',
       'dst2src_first_seen_ms','dst2src_last_seen_ms']

#0
master_protocol=['unkown']
master_protocol_set_list=[set(),]
#1
app_protocol=['unkown']
app_protocol_set_list=[set(),]
#2
application_name=['unkown']
application_name__set_list=[set(),]
#3
category_name=['unkown']
category_name__set_list=[set(),]
#4
client_info=['unkown']
client_info__set_list=[set(),]
#5
server_info=['unkown']
server_info__set_list=[set(),]
#6
src_ip=['unkown']
src_ip_set_list=[set(),]
#7
dst_ip=['unkown']
dst_ip_set_list=[set(),]
#8
src_port=['unkown']
src_port_set_list=[set(),]
#9
dst_port=['unkown']
dst_port_set_list=[set(),]
#10
vlan_id=['unkown']
vlan_id_set_list=[set(),]



attrlist=[
     master_protocol,
    app_protocol,
    application_name,
    category_name,
    client_info,
    server_info,
    src_ip,
    dst_ip,
    src_port,
    dst_port,
    vlan_id
]

setlist=[
   master_protocol_set_list,
    app_protocol_set_list,
    application_name__set_list,
    category_name__set_list,
    client_info__set_list,
    server_info__set_list,
    src_ip_set_list,
    dst_ip_set_list,
    src_port_set_list,
    dst_port_set_list,
    vlan_id_set_list
]


def judge(df, index, hashOfAttr, indexName,f):
    idOfAttr= df.loc[index,names[indexName]]
    if pd.isna(idOfAttr):
        setlist[indexName][0].add(f.split(".")[0]+"-"+str(index))
    else:
        if idOfAttr not in hashOfAttr:
            hashOfAttr.append(idOfAttr)
            x=set()
            x.add(f+"-"+str(index))
            setlist[indexName].append(x)
        else:
            search_index=hashOfAttr.index(idOfAttr)
            setlist[indexName][search_index].add(f.split(".")[0]+"-"+str(index))

def createData(df):
    # timeDelay=[]
    # for i in range(len(df)):
    #     flowStart=int(df.loc[i,'bidirectional_first_seen_ms'])
    #     flowEnd=int(df.loc[i,'bidirectional_last_seen_ms'])
    #     t=flowEnd-flowStart
    #     tt=int(df.loc[i,'bidirectional_duration_ms'])
    #     print(t," ",tt)
    #     timeDelay.append(t)
    # df['time_delay']=list(timeDelay)


    # for i in range(len(df)):
    #     if not df.loc[i,'application_name'] == "Network":
    #         df.drop([i],inplace=True)

    # df.drop(columns=['Unnamed: 0','application_name','category_name','client_info','server_info','j3a_client','j3a_server',
    #                  'src_ip','dst_ip','bidirectional_first_seen_ms','bidirectional_last_seen_ms','src2dst_first_seen_ms',
    #                  'src2dst_last_seen_ms','dst2src_first_seen_ms','dst2src_last_seen_ms'], inplace=True)

    # if not os.path.exists("D://Python_code/NetTraAnalysis/Network.csv"):
    df.to_csv("Network.csv")
    # else:
    #     df.to_csv("Network.csv",mode='a+',header=False)


def judgeInfo(df,f):
    # for i in range(len(df)):
    for i in range(100):
        #判断主协议类型
        judge(df,i,master_protocol,0,f)
        #判断app协议类型
        judge(df,i, app_protocol,1,f)
        #判断应用名称
        judge(df,i,application_name,2,f)
        #判断应用类别
        judge(df,i, category_name,3,f)
        #判断客户端信息
        judge(df,i, client_info,4,f)
        #判断服务端信息
        judge(df,i, server_info,5,f)
        #ip分类
        judge(df, i, src_ip, 6,f)
        judge(df, i, dst_ip, 7,f)
        #端口分类
        judge(df, i, src_port, 8, f)
        judge(df, i, dst_port, 9, f)

        #vlan分类
        judge(df,i,vlan_id,10,f)
    with open("./res.txt",'w') as f:
        for i in range(11):
            f.write(str(setlist[i])+"\n")

def drawPie(data,i,d):
    #print(data.values())
    wedges, texts=plt.pie(x=d)
    plt.legend(wedges,
               data.keys(),
               fontsize=6,
               title="proportion",
               loc="center right",)
               # bbox_to_anchor=(0.91, 0, 0.3, 1))
    plt.savefig("./Image/"+i+".png")
    plt.close()
    # fig = plt.figure()
    # plt.table()
    # the_table = plt.table(cellText=data.values(), rowLabels=data.keys(), colLabels=data.values(),
    #                       colWidths = [0.1] * vals.shape[1], loc = 'center', cellLoc = 'center')
def displayMap(df,attr,index,f):
    for i in range(len(df)):
        judge(df, i, attr,index,f)
    name=list(attr.keys())
    value=list(attr.values())
    with open("buffer.txt", 'w')as f:
        for i in range(len(name)):
            f.write(str(name[i]))
            f.write(" ")
            f.write(str(value[i]))
            f.write("\n")

if __name__=="__main__":
    # for i in range(11):
    for f in os.listdir("./data"):
        #f="0708103916.csv"
        df = pd.read_csv("./data/"+f)
        judgeInfo(df,f)
        for i in range(11):
            key=attrlist[i]
            value=setlist[i]
            json_dict = {}
            for j in range(len(key)):

                json_dict[str(key[j])]=list(value[j])

            print(json_dict)
            with open(names[i]+'.json', 'w') as fw:
                json.dump(json_dict,fw,indent=4)
        # os.chdir("./")
        # for file in glob.glob("*.json"):
        #     #print(file)
        #     with open(file)as f:
        #         d = json.load(f)
        #
        #         data=[]
        #         for key in d.keys():
        #             data.append(len(d[key]))
        #             #print(key,len(d[key]))
        #         print(f.name)
        #         drawPie(d, f.name.split(".")[0],data)
        #         f.close()

        # print(master_protocol)
        # print(app_protocol)
        # print(application_name)
        # print(category_name)
        # print(client_info)
        # print(server_info)
        # print(src_ip)
        # print(dst_ip)
        # # drawPie(master_protocol, 0)
        # # drawPie(app_protocol, 1)
        # # drawPie(application_name, 2)
        # # drawPie(category_name,3)
        # # drawPie(client_info,4)
        # # drawPie(server_info,5)
        # drawPie(src_ip, 6)
        # drawPie(dst_ip, 7)
        # displayMap(df,dst_port,9)

        #createData(df)

