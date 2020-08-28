from pyod.models.knn import KNN
from pyod.models.auto_encoder import AutoEncoder
from pyod.models.abod import ABOD
from pyod.models.hbos import HBOS
from pyod.models.lof import LOF
from pyod.models.iforest import IForest
from pyod.models.lscp import LSCP
from pyod.models.mcd import MCD
from pyod.models.mo_gaal import MO_GAAL
from pyod.models.ocsvm import OCSVM
from pyod.models.sod import SOD
from pyod.models.sos import SOS
from pyod.models.vae import VAE
from pyod.models.xgbod import XGBOD
from keras.losses import mean_squared_error
from keras.optimizers import adam
import joblib
from configparser import ConfigParser

class AbnomalDector():
    def __init__(self,algorithm_list):
        self._contamination=0.1
        '''
        最小方差行列式算法（寻找包含H个样本的最优椭球体）
        '''
        self.mcd=MCD(store_precision=True,#保存精度值
                     assume_centered=True,#保证趋于0的特征稳定性
                     contamination=self._contamination,#异常值比例
                 )
        '''
        基于角度量的异常检测
        '''
        self.abod=ABOD(contamination=self._contamination,#异常值的比例
                       n_neighbors=20,#用于判定的邻居个数
                       method='fast' # 使用方法，fast=>只考虑邻居个数的点
                        )
        '''
        自编码器异常检测
        '''
        self.ae=AutoEncoder(
                        hidden_neurons=[64,32,32,64],#隐藏层单元个数
                        hidden_activation='relu',#隐藏层激活函数
                        output_activation='sigmoid',#输出层激活函数
                        loss=mean_squared_error,#损失函数
                        optimizer=adam,#优化器
                        epochs=1000,#训练轮数
                        batch_size=20,#批量
                        dropout_rate=0.2,#dropout概率
                        l2_regularizer=0.1,#l2正则化
                        validation_size=0.2,#验证集比例
                        preprocessing=True,#归一化
                        verbose=1,#过程显示
                        contamination=self._contamination #异常值的比例
                        )
        '''
        直方图异常检测算法
        '''
        self.hbos=HBOS(
                        n_bins=30,#区间个数
                        alpha=0.1,#正则化项
                        contamination=self._contamination,#异常值比例
                        )
        '''
        孤立森林算法
        '''
        self.iforest=IForest(
                        n_estimators=100,#孤立树的个数
                        max_samples='auto',#采样数量为min(256,n_sample)
                        max_features=20,#采样的特征数
                        bootstrap=False,#是否有放回取样
                        n_jobs=4,#线程个数
                        verbose=1,#过程显示
                            )
        '''
        局部异常检测
        '''
        self.lof=LOF(
                        n_neighbors=20,#邻居个数
                        algorithm="ball_tree",#最近邻优化方法
                        leaf_size=100,#叶结点的数量
                        metric='euclidean',#距离的度量函数
                        n_jobs=4,#线程的数量
                    )


        '''
        生成对抗主动学习的无监督异常检测
        '''
        self.mogaal=MO_GAAL(
                        contamination=self._contamination,#异常比例
                        stop_epochs=100,#迭代次数
                        lr_d=0.01,#判别器学习率
                        lr_g=0.0001,#生成器学习率
                        decay=1e-6,#随机梯度下降衰减速率
                        momentum=0.9,#随机梯度下降动量比例
                        )
        '''
        one-class SVM
        '''
        self.ocsvm=OCSVM(
                        kernel='rbf',#高斯径向基核函数
                        nu=0.5,
                        gamma='auto',
                        cache_size=64,#核函数缓存
                        max_iter=2000,
                        contamination=self._contamination
        )
        '''
        子空间异常检测
        '''
        self.sod=SOD(
                    n_neighbors=20,#邻居个数
                    ref_set=15,
                    alpha=0.8,
                    contamination=self._contamination
        )
        '''
        随机异常检测（关联度检测）
        '''
        self.sos=SOS(
                    contamination=self._contamination,
                    perplexity=4,
                    metric='euclidean',
        )
        '''
        变分自编码器
        '''
        self.vae=VAE(
                    encoder_neurons=[32, 16, 8],#编码隐藏层
                    decoder_neurons=[8,16,32],#解码隐藏层
                    hidden_activation='relu',#隐藏层激活函数
                    output_activation='sigmoid',#输出层激活函数
                    loss=mean_squared_error,#损失函数
                    gamma=1,
                    capacity=1,
                    optimizer=adam,
                    epochs=500,
                    batch_size=16,
                    dropout_rate=0.2,
                    l2_regularizer=0.1,
                    validation_size=0.2,
                    preprocessing=True,
                    verbosity=1,
                    contamination=0.1
                    )
        '''
        基于XGboost的异常检测
        '''
        self.xgbod=XGBOD(
                    estimator_list=[self.abod, self.iforest, self.hbos,
                           self.lof, self.mcd,self.hbos,self.ocsvm,
                           self.sos,self.ae,self.vae,self.mogaal],
                    standardization_flag_list=[True,True,True,True,
                                               True, True,True,True,
                                               True, True],
                    max_depth=20,
                    learning_rate=0.1,
                    n_estimators=200,
                    silent=False,
                    booster='gbtree',
                    n_jobs=4,
                    min_child_weight=0,
                    max_delta_step=10,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    colsample_bylevel=0.8,
                    reg_alpha=1,
                    reg_lambda=1,
                    scale_pos_weight=0.9,
                    base_score=0.5,
                    )
        '''
        局部异常选择并行集成算法
        '''
        self.lscp = LSCP(
            detector_list=[self.abod, self.iforest, self.hbos,
                           self.lof, self.mcd,self.hbos,self.ocsvm,
                           self.sos,self.sod],  # 基础异常检测算法
            local_region_size=20,  # 最近邻的个数
            local_max_features=0.8,  # 采样的特征比例
            n_bins=15,  # local_region个数
            random_state=0,  # 随机常数
            contamination=self._contamination,  # 异常比例
        )

        self._model_list=[]
        for al in algorithm_list:
            if hasattr(self,al):
                self._model_list.append(getattr(self,al))

        conf = ConfigParser()
        conf.read("./config/config.ini")
        try:
            value=conf['default']['od_rate']
            if self.isfloat(value):
                self.rate = int(len(self._model_list)*float(value))
            elif int(value) <= len(self._model_list):
                self.rate=int(value)
            else:
                raise Exception("parameter 'od_rate' error")
        except:
            raise Exception("expect 'od_rate' in config.ini ")
    '''
    模型训练
    '''
    def _models_train(self,X_train,app):

        for model in self._model_list:
            model.fit(X_train)
            joblib.dump(model,app+str("-")+str(model.__class__.__name__)+".model")

    '''
    模型预测
    '''
    def _model_predict(self,data):
        res=0
        for model in self._model_list:
            r=model.predict(data)
            res=res+r
        if res>self.rate:
            return True
        else:
            return False

    def isfloat(self,str_number):
        try:
            int(str_number)
            return False
        except ValueError:
            return True