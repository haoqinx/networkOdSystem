from sklearn.decomposition import PCA
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.cluster import KMeans
from sklearn.metrics import calinski_harabaz_score,silhouette_score
from scipy.spatial.distance import cdist

'''
使用CH值和轮廓系数 评价聚类效果
'''
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
    plt.plot(range(1,10),result,'gx-')
    plt.savefig("肘部法")
    plt.plot(range(1,10),score,'r*-')
    plt.savefig("轮廓系数")
    return label

def display(data,i,label=[]):
    fig = plt.figure()
    dim=len(data[0])
    if(len(label)==0):
        for i in range(len(data)):
            label.append(0)
    if(dim==3):
        ax = Axes3D(fig)
        x=data[:,0]
        y=data[:,1]
        z=data[:,2]
        ax.scatter(x,y,z,c=label)
        ax.set_zlabel('Z', fontdict={'size': 15, 'color': 'red'})
        ax.set_ylabel('Y', fontdict={'size': 15, 'color': 'red'})
        ax.set_xlabel('X', fontdict={'size': 15, 'color': 'red'})
        # plt.show()
        plt.title("dim3")
        plt.savefig("pca3"+str(i)+".png")

    else:
        x = data[:, 0]
        y = data[:, 1]
        plt.scatter(x,y,c=label)
        plt.title("dim2")
        #plt.show()
        plt.savefig("pca2" + str(i) + ".png")

def dataPca(df,dim):
    data=np.array(df)
    pca=PCA(n_components=dim)
    #data=pca.fit(data)
    data1=pca.fit_transform(data)
    print("系统的pca：",data1)

    print("方差:"+str(pca.explained_variance_))
    print("方差比值:"+str(pca.explained_variance_ratio_))

    return data

def myPCA(df,dim):

    data=np.array(df)


    meanValues = np.mean(data, axis=0)  # 竖着求平均值，数据格式是m×n
    meanRemoved = data - meanValues  # 0均值化  m×n维


    covMat = np.cov(meanRemoved, rowvar=False)  # 每一列作为一个独立变量求协方差  n×n维
    eigVals, eigVects = np.linalg.eig(np.mat(covMat))  # 求特征值和特征向量  eigVects是n×n维
    eigValInd = np.argsort(-eigVals)  # 特征值由大到小排序，eigValInd十个arrary数组 1×n维
    print(eigValInd)
    eigValInd = eigValInd[:dim]  # 选取前topNfeat个特征值的序号  1×r维
    redEigVects = eigVects[:, eigValInd]  # 把符合条件的几列特征筛选出来组成P  n×r维
    lowDDataMat = meanRemoved * redEigVects  # 矩阵点乘筛选的特征向量矩阵  m×r维 公式Y=X*P
    reconMat = (lowDDataMat * redEigVects.T) + meanValues  # 转换新空间的数据  m×n维

    print("自己实现的pca:",lowDDataMat)
    return lowDDataMat, reconMat

def myPCA2(data,n_dim):
    data = data - np.mean(data, axis=0, keepdims=True)

    cov = np.dot(data.T, data)

    eig_values, eig_vector = np.linalg.eig(cov)
    # print(eig_values)
    indexs_ = np.argsort(-eig_values)[:n_dim]
    picked_eig_values = eig_values[indexs_]
    picked_eig_vector = eig_vector[:, indexs_]
    data_ndim = np.dot(data, picked_eig_vector)
    print(data_ndim)
    return data_ndim

if __name__=="__main__":
    # df=pd.read_csv("source.csv")
    # dimOfPca=3
    # data=dataPca(df,dimOfPca)
    # label=doCluster(data)
    # for i in range(2,10):
    #     display(data,i-2,label[i-2])

    # df = pd.read_csv("amazon.csv")
    # dimOfPca = 3
    # data = dataPca(df, dimOfPca)

    df=pd.read_csv("amazon.csv")
    df.drop(columns=['id',  'app_protocol', 'master_protocol', 'src_port', 'dst_port', 'vlan_id',
                     'src_ip_type', 'dst_ip_type'], inplace=True)

    myPCA(np.array(df),3)

    dimOfPca = 3
    data = dataPca(df, dimOfPca)

    # label = doCluster(data)
    # for i in range(2, 10):
    #     display(data, i - 2, label[i - 2])