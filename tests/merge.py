# import glob
#
# csvx_list = glob.glob('target*.csv')
# print('总共发现%s个CSV文件'% len(csvx_list))
# print(csvx_list )
#
# print('正在处理............')
# for i in csvx_list:
#     fr = open(i,'rb').read()
#     with open('global.csv','ab') as f:
#         f.write(fr)
# df=pd.read_csv("global.csv")
# print(len(df))
import multiprocessing
import pandas as pd
import pymysql
import numpy as np

attrlist=[0,0,'int', 'int', 'int', 'int', 'int', 'int', 'str', 'int', 'str',
          'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int',
          'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int',
          'int', 'int', 'float', 'float', 'int', 'int', 'float', 'float',
          'int', 'int', 'float', 'float', 'int', 'int', 'float', 'float',
          'int', 'int', 'float', 'float', 'int', 'int', 'float', 'float',
          'int', 'int', 'float', 'float', 'int', 'int', 'float', 'float',
          'int', 'int', 'float', 'float', 'int', 'int', 'int', 'int', 'int',
          'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int',
          'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int',
          'int', 'int', 'int', 'int', 'str', 'str', 'str', 'str', 'str', 'str']



LENGTH=1082846

# 一个根据pandas自动识别type来设定table的type
def make_table_sql(df):
    attrExample = df.iloc[2,:]

    # 添加id 制动递增主键模式
    make_table = ""

    for i in range(2,len(attrExample)):
        t=type(attrExample[i])


        if np.int64 == t:
            char = df.keys()[i] + ' INT(20),'

            attrlist.append("int")
            make_table += char
        elif np.float64 == t:
            char = df.keys()[i] + ' FLOAT,'
            attrlist.append("float")
            make_table += char
        elif np.float == t or np.str == t:
            char = df.keys()[i] + ' VARCHAR(255),'
            print(char)
            attrlist.append("str")
            make_table+=char

    sql="create table stream( id int auto_increment primary key,"+make_table
    sql=sql[:-1]+");"
    print(len(attrlist))
    print(sql)
    return sql

#向sql中插入数据
def insertSQL(row):
    sql = "insert into stream values(null,"

    for i in range(2,len(row)):

        attr=row[i]
        if(attrlist[i] == "str"):
            try:
                if(len(attr)>255):
                    attr=attr[:254]
            except:
                print("float")
            attr="'"+str(attr)+"',"
        else:
            attr=str(attr)+","
        sql +=attr

    return sql[:-1]+");"

#连接数据库
def connect():
    con = pymysql.connect(user="root",
                          passwd="0215",
                          db="NetStream",
                          host="127.0.0.1",
                          local_infile=1,
                          port=3306
                          )
    # con.set_charset('utf8')
    # cur = con.cursor()
    # cur.execute("set names utf8")
    # cur.execute("SET character_set_connection=utf8;")
    return con
#所有数据插入数据库
def csv2mysql():
    con=connect()
    cur=con.cursor()
    for index in range(3,19):
        df = pd.read_csv("target" + str(index) + ".csv")

        for i in range(len(df)):
            sql=insertSQL(df.iloc[i,:])
            print(sql)
            try:
                cur.execute(sql)
            except:
                print("error")
        con.commit()

def find(attr):
    sql="select "+attr+" from stream;"
    con=connect()
    cur=con.cursor()
    data=cur.execute(sql)
    print(data)
def solve(index):

     df=pd.read_csv("target"+str(index)+".csv")

     print(len(df.loc[0]))
     for i in range(len(df.loc[0,:])):
         print(type(df.iloc[5,i])==np.float64)

def countAttr(con):
    cur=con.cursor()

if __name__=="__main__":
    # pool=multiprocessing.Pool(processes=21)
    # for i in range(22):
    #     pool.apply(solve,(i,))
    # pool.close()
    # pool.join()
    '''
    下面是连接 数据库并按照csv文件属性顺序创建表stream
    '''
    # df=pd.read_csv("target.csv")
    # sql=make_table_sql(df=df)
    # print(sql)
    # con=connect()
    # con.cursor().execute(sql)
    '''下面是将数据插入数据库
    '''
    # csv2mysql()
    '''
    访问表中的数据
    '''
    find("src2dst_first_seen_ms")