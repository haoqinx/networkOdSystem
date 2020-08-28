from util.dealWithStream import DWS
from util.esTransmission import Estransmission
from util.od import AbnomalDector
from util.dataPretreatment import DataPretreatment
from threading import Thread,Condition
import queue
from concurrent.futures import ThreadPoolExecutor
from configparser import ConfigParser
from redis import ConnectionPool
import time
import psutil
import json
import joblib

APP_LIST=[
    'HTTP.TikTok',
]

'''
very import !!!!
add new global announce here,aim to control model iteration
keys must be the same as APP_LIST
'''
MODEL_FLAG_TIKTOK = 0 #range is 0,1
MODEL_LIST={
    'HTTP.TikTok':MODEL_FLAG_TIKTOK,
}
'''
algorithm list 
'''
ALGORITHM_LIST=[
        "iforest",#孤立森林算法
        "lscp", #局部异常选择并行集成算法
        "hbos",#直方图异常检测算法
        "sod",#子空间异常检测
'''
下列为备选算法，有需要时提前训练模型保存至../models文件夹下 取消注释即可
'''
        # "mcd",#最小方差行列式算法（寻找包含H个样本的最优椭球体）
        # "abod", #基于角度量的异常检测
        # "ae",#自编码器异常检测
        # "lof",#局部异常检测
        # "mogaal",#生成对抗主动学习的无监督异常检测
        # "ocsvm",#one-class SVM
        # "sos",#随机异常检测（关联度检测）
        # "vae",#变分自编码器
        # "xgbod",#基于XGboost的异常检测

]

ATTR_LIST=[
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


class CountDownLatch():
    '''
    thread synchronization
    '''
    def __init__(self,count):
        self.count=count
        self.condition=Condition()
    def await(self):
        try:
            self.condition.acquire()
            while self.count>0:
                self.condition.wait()
        finally:
            self.condition.release()
    def countDown(self):
        try:
            self.condition.acquire()
            self.count-=1
            self.condition.notifyAll()
        finally:
            self.condition.release()
    def get_count(self):
        return self.count

'''
性能测试:时间
'''
def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        print(func.__name__+'共耗时约 {:.2f} 秒'.format(time.time() - start))
        return res
    return wrapper

'''
内存、cpu、磁盘信息
'''
# def systemStatus(func):
#     def wrapper(*args,**kwargs):
#         mem = psutil.virtual_memory().percent
#         cpu_status = psutil.cpu_times()
#         disk_status = psutil.disk_usage("./").percent
#         res = func(*args, **kwargs)
#         memd=psutil.virtual_memory().percent
#         cpu_statusd = psutil.cpu_times()
#         disk_statusd = psutil.disk_usage("./").percent
#         return res
#     return  wrapper

@timer
def model_controller(model_first,model_second,data_pretreatment,cycle,elasticsearch):
    '''
    :param model_first: 第一个模型集合列表
    :param model_second: 第二个模型集合列表
    :param data_pretreatment: 数据辅助类
    :param cycle: 迭代周期（天）
    :param elasticsearch: es对象
    :return: None
    '''
    global MODEL_LIST
    for i,odclass in enumerate(model_first):
        for j,model in enumerate(MODEL_LIST):
            model_first[i]._model_list[j] = joblib.load("./models/" + APP_LIST[i] + str("-") + str(model.__class__.__name__) + ".model")
            model_first[i]._model_list[j] = joblib.load("./models/" + APP_LIST[i] + str("-") + str(model.__class__.__name__) + ".model")
    start=time.time()
    while True:
        currentTime = time.time()
        if start + cycle*24*60*60 < currentTime:
            start = currentTime
            for app in MODEL_LIST.keys():
                index = APP_LIST.index(app_name)
                data = data_pretreatment.getData(app)
                if MODEL_LIST[app] == 1:
                    model_first[index]._models_train(data,app)
                elif MODEL_LIST[app] == 0:
                    model_second[index]._models_train(data,app)
                else:
                    raise RuntimeError("except 0 or 1 of "+str(app)+" flag,but get "+
                                       str(MODEL_LIST[app])+" instead")
                MODEL_LIST[app] = 1 - MODEL_LIST[app]
                slide_controller(elasticsearch,app)
                data_pretreatment.deleteData(app)

@timer
def slide_controller(elasticsearch,app):
    '''
    :param elasticsearch: es类
    :param app: 应用名称
    :return: None
    只向es中添加数据
    '''
    elasticsearch.redis2es(app)


if __name__ == '__main__':
    '''
    初始化信号量 用于线程同步
    初始化线程池
    '''
    thread_pool = ThreadPoolExecutor(1000)
    latch = CountDownLatch(count=2)

    '''
    初始化redis连接池
    '''
    conf = ConfigParser()
    conf.read("./config/config.ini")
    try:
        port = int(conf['default']['redis_port'])
        pool = ConnectionPool(host='localhost', port=port, decode_responses=True)
    except ValueError as e:
        raise RuntimeError("fail to connect redis, please check the parameter again") from e


    '''
    初始化工作：
    ---处理csv文件
    ---建立索引
    ---上传csv文件
    '''
    try:
        _csv_dir=conf['default']['csv_dir']
    except:
        _csv_dir=""

    es = Estransmission(12,[],"./config/base.txt",attrlist=ATTR_LIST,pool=pool)

    dws = DWS(pool=pool,attrlist=ATTR_LIST)

    _data_pretreatment=DataPretreatment(pool=pool,attrlist=ATTR_LIST)

    if _csv_dir == "":
        for app in APP_LIST:
            es.createIndex(app)
            es.redis2es(app)
    else:
        for file in _csv_dir:
            es.solveCSV(_csv_dir+file)
            es.createIndex(file.split(".")[0])
            es.sendCSV(_csv_dir+file)

    '''
    ----目标：迭代异常检测类（每个应用两个模型）
    ----思路：初始化两个模型列表，分别对应每个应用的模型1和模型2，载入预训练的算法模型，模型1用于第t个周期的预测 
    第t个周期结束时将第t个周期的数据训练模型2，同理第t+1周期使用模型2预测，t+1周期内数据迭代新的模型1，以此类推
    ----
    '''
    try:
        cycle = int(conf['default']['cycle'])
    except ValueError as e:
        raise RuntimeError("expect a model cycle in config.ini") from e
    _model_first=[]
    _model_second=[]

    for app in APP_LIST:
        _od_algorithms_first = AbnomalDector(MODEL_LIST)
        _od_algorithms_second = AbnomalDector(MODEL_LIST)
        _model_first.append(_od_algorithms_first)
        _model_second.append(_od_algorithms_second)

    '''
    控制异常检测模型迭代
    '''
    thread_pool.submit(model_controller,_model_first,_model_second,_data_pretreatment,cycle,es)
    # '''
    #   控制滑动窗口模型定时更新的线程
    # '''
    # thread_pool.submit(slide_controller, (es))

    # for app in app_list:
    #     data=_data_pretreatment.getData(app)
    #     _od_algorithms_first._models_train(data, app)

    '''
    网络流缓冲区 使用线程安全的队列 写入时不阻塞 读取有锁
    第一个缓冲区中为滑动窗口模型的json序列;
    第二个缓冲区为异常检测算法的numpy数组
    '''
    _buffer_slide=queue.Queue()
    _buffer_od=queue.Queue()

    ''' 
    网卡监控程序，对数据进行捕获并将数据添加到缓冲区
    '''

    thread_pool.submit(dws.run,_buffer_slide,_buffer_od)
    print("start capturing--------------------------------------------")

    '''
    设置两个线程池
    检查程序将网络流与滑动数据进行比较，将网络流数据送入异常检查程序判定 
    '''
    while True:
        try:
            if not (_buffer_slide.empty() and _buffer_od.empty()):
                flow = json.loads(_buffer_slide.get())
                _slide_res=thread_pool.submit(es.slidwindowOD,flow)
                app_name = flow['application_name']
                flow_matrix=_buffer_od.get()
                index = APP_LIST.index(app_name)
                if MODEL_LIST[app_name] == 0:
                    _od_res = thread_pool.submit(_model_first[index]._model_predict(flow_matrix))
                elif MODEL_LIST[app_name] == 1:
                    _od_res = thread_pool.submit(_model_second[index]._model_predict(flow_matrix))
                else:
                    raise RuntimeError("except 0 or 1 of "+str(app_name)+" flag,but get "+str(MODEL_LIST[app_name])+" instead")

                if _slide_res or _od_res:
                    with open("./log/"+str(app_name),"a+")as f:
                        f.write(str(flow))
                    pass

        except Exception as e:
            raise RuntimeError("error when detecting flow")from e

        # _check_thread=Thread(target=es.slidwindowOD(buffer,))
        # _check_thread.start()


