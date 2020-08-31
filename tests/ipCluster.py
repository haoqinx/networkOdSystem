import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import calinski_harabaz_score,silhouette_score
from scipy.spatial.distance import cdist

def str2ip(ipstr):
    items = [int(x) for x in ipstr.split(".")]
    return sum([items[i] << [24, 16, 8, 0][i] for i in range(4)])


def doCluster(X_train):
    result=[]
    score=[]
    label=[]
    for k in range(2,10):
        kmeans = KMeans(n_clusters=k)
        y_pred=kmeans.fit_predict(X_train)
        result.append(sum(np.min(cdist(X_train,kmeans.cluster_centers_,'euclidean'),axis=1)/X_train.shape[0]))
        score.append(silhouette_score(X_train,kmeans.labels_,metric='euclidean'))
        print('这个是k={}次时的CH值：'.format(k), calinski_harabaz_score(X_train, y_pred))
        print('这个是k={}次时的轮廓系数：'.format(k), silhouette_score(X_train, y_pred, metric='euclidean'))
        label.append(y_pred)
    plt.plot(range(2,10),result,'gx-')
    plt.savefig("肘部法")
    plt.plot(range(2,10),score,'r*-')
    plt.savefig("轮廓系数")
    return label

if __name__=="__main__":
    data=[]
    os.chdir("./data/")
    for file in glob.glob("*.csv"):
        df=pd.read_csv("./"+file)
        for i in range(100):
            d=[]
            ip=df.iloc[i]['src_ip']
            ip=str2ip(ip)
            d.append(ip)
            data.append(d)

    data=np.array(data)
    data.reshape(-1, 1)
    print(data.shape)
    label=doCluster(data)
    for i in range(len(label)):
        with open("srcipCluster"+str(i+2)+".txt",'a')as f:
            f.write(str(label[i]))
            f.write("\n")

