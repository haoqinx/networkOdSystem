from elasticsearch import Elasticsearch,helpers
import csv
import pandas as pd
from configparser import ConfigParser
import json
from redis import Redis
class Estransmission():

    def __init__(self,threshold,param,timeBasefile,attrlist,pool):
        conf=ConfigParser()
        conf.read("./config/config.ini")
        try:
            self.slideCycle=int(conf['default']['slideCycle'])
        except Exception as e:
            raise RuntimeError("expect a integer value for slide window algorithm") from e
        try:
            self.es=Elasticsearch('http://localhost:9200')
        except Exception as e:
            raise RuntimeError("expect service ElasticSearch running on port 9200") from e
        try:
            self.windowSize=int(conf['default']['window'])
            if self.windowSize & 1 == 0:
                raise ValueError("expect a add number for window size")
        except Exception as e:
            raise RuntimeError("error when parsing window size from config.ini file")

        self.threshold=threshold
        self.param=param

        self.attrlist=attrlist
        self._base_time = dict()
        with open(timeBasefile)as f:
            lines = f.readlines()
            for line in lines:
                self._base_time[line.split(":")[0]] = line.split(":")[1]
        self.r= Redis(connection_pool=pool)

    def getBaseTime(self, classifyName):
        return int(self._base_time[classifyName])

    def redis2es(self, app):
        ACTIIONS = []
        data = self.r.lrange(str(app), 0, -1)
        # len = r.llen(str(app))
        # if 0 < len < 10000:
        #     epoch = 0
        # elif len > 10000:
        #     epoch = len/10000
        # else:
        #     raise RuntimeError("the length of a redis list must > 0 ,get"+str(len)+"instead")
        basetime = self.getBaseTime(app)

        for item in data:
            record = json.loads(item)
            '''
            将时间转换成相对时间
            '''
            while record['bidirectional_first_seen_ms'] > basetime:
                record['bidirectional_first_seen_ms'] -= 60 * 60 * 24 * self.slideCycle
            record['bidirectional_first_seen_ms'] += basetime
            action = {
                "_index": self.changeTolowerCase(str(app)),
                "_type": "none",
                "_source": {
                    "bidirectional_first_seen_ms":record['bidirectional_first_seen_ms'],
                    "bidirectional_duration_ms":record['bidirectional_duration_ms'],
                    "bidirectional_ip_bytes":record['bidirectional_ip_bytes'],
                    "bidirectional_max_piat_ms":record['bidirectional_max_piat_ms'],
                    "bidirectional_mean_piat_ms":record['bidirectional_mean_piat_ms'],
                    "bidirectional_min_piat_ms":record['bidirectional_min_piat_ms'],
                    "bidirectional_packets":record['bidirectional_packets'],
                    "bidirectional_raw_bytes":record['bidirectional_raw_bytes'],
                    "bidirectional_stdev_piat_ms":record['bidirectional_stdev_piat_ms'],
                    "dst2src_ack_packets":record['dst2src_ack_packets'],
                    "dst2src_duration_ms":record['dst2src_duration_ms'],
                    "dst2src_ip_bytes":record['dst2src_ip_bytes'],
                    "dst2src_max_piat_ms":record['dst2src_max_piat_ms'],
                    "dst2src_mean_piat_ms":record['dst2src_mean_piat_ms'],
                    "dst2src_packets":record['dst2src_packets'],
                    "dst2src_raw_bytes":record['dst2src_raw_bytes'],
                    "src2dst_ack_packets":record['src2dst_ack_packets'],
                    "src2dst_duration_ms":record['src2dst_duration_ms'],
                    "src2dst_ip_bytes":record['src2dst_ip_bytes'],
                    "src2dst_mean_piat_ms":record['src2dst_ip_bytes'],
                    "dst2src_min_raw_ps":record['dst2src_min_raw_ps'],
                    "src2dst_raw_bytes":record['src2dst_raw_bytes'],
                    "src2dst_stdev_piat_ms":record['src2dst_stdev_piat_ms']
                }
            }
            ACTIIONS.append(action)
        helpers.bulk(self.es, ACTIIONS, index=str(app))

    def changeTolowerCase(self,string):
        '''
        索引必须是小写
        :param string:文件名称
        :return: 转化后的字符串
        '''
        return string.lower()

    def createIndex(self,filename):
        '''
        创建新索引
        :param filename: 索引名称
        :return: 是否创建成功
        '''
        _index_name=filename.split(".")[0].lower()
        #_index_name=self.changeTolowerCase(_index_name)
        #_index_name=filename
        _index_mapping={
            "mappings":{
                    "properties":{
                        "bidirectional_first_seen_ms":{
                            'type':'long'
                        },
                        "bidirectional_duration_ms": {
                            'type': 'float'
                        },
                        "bidirectional_ip_bytes": {
                            'type': 'float'
                        },
                        "bidirectional_max_piat_ms": {
                            'type': 'float'
                        },
                        "bidirectional_mean_piat_ms": {
                            'type': 'float'
                        },
                        "bidirectional_min_piat_ms": {
                            'type': 'float'
                        },
                        "bidirectional_packets": {
                            'type': 'float'
                        },
                        "bidirectional_raw_bytes": {
                            'type': 'float'
                        },
                        "bidirectional_stdev_piat_ms": {
                            'type': 'float'
                        },
                        "dst2src_ack_packets": {
                            'type': 'float'
                        },
                        "dst2src_duration_ms": {
                            'type': 'float'
                        },
                        "dst2src_ip_bytes": {
                            'type': 'float'
                        },
                        "dst2src_max_piat_ms": {
                            'type': 'float'
                        },
                        "dst2src_mean_piat_ms": {
                            'type': 'float'
                        },
                        "dst2src_packets": {
                            'type': 'float'
                        },
                        "dst2src_raw_bytes": {
                            'type': 'float'
                        },
                        "src2dst_ack_packets": {
                            'type': 'float'
                        },
                        "src2dst_duration_ms": {
                            'type': 'float'
                        },
                        "src2dst_ip_bytes": {
                            'type': 'float'
                        },
                        "src2dst_mean_piat_ms": {
                            'type': 'float'
                        },
                        "dst2src_min_raw_ps": {
                            'type': 'float'
                        },
                        "src2dst_raw_bytes": {
                            'type': 'float'
                        },
                        "src2dst_stdev_piat_ms": {
                            'type': 'float'
                        }


                }
            }

        }

        try:
            res=self.es.indices.create(index=_index_name, body=_index_mapping)
        except:
            self.es.indices.delete(index=_index_name)
            res=self.es.indices.create(index=_index_name,body=_index_mapping)
        print(res)

    def sendCSV(self,filename):
        '''
        :param filename: 文件名称
        :return: defult:None
        '''

        with open(filename,'r')as f:
            reader=csv.DictReader(f)
            helpers.bulk(self.es,reader,index = filename.split(".")[0].lower())
            print("finished....")

    def solveCSV(self, file):
        df = pd.read_csv(file)
        try:
            df.drop(columns=["Unnamed: 0"], inplace=True)
            df.drop([0, 1, len(df) - 1, len(df) - 2], inplace=True)
            df.to_csv(file, index=False)
        except:
            pass

    def slidwindowOD(self,flow):
        # _find_early_flow_body={"query": {"range":{"bidirectional_first_seen_ms":{"lt":1594188082605}}},"aggs":{"min_time":{"min":{"field":"bidirectional_first_seen_ms"}}}}
        # _find_later_flow_body={"query": {"range":{"bidirectional_first_seen_ms":{"gt":1594188082605}}},"aggs":{"max_time":{"min":{"field":"bidirectional_first_seen_ms"}}}}

        '''
        :param buffer: 缓冲区
        :return: 是否异常
        '''
        time=flow['bidirectional_first_seen_ms']
        file=flow['application_name']+".csv"
        basetime=self.getBaseTime(flow['application_name'])

        while(time > basetime):
            time-=60*60*24*self.slideCycle
        time += basetime

        #_window_size = int(file.split("-")[-1])/2
        _window_size=self.windowSize
        _find_early_flow_body = {"size":_window_size,"query": {"range":{"bidirectional_first_seen_ms": {"lte": time}}},"sort":{"bidirectional_first_seen_ms":{"order":"desc"}}}
        _find_later_flow_body = {"size":_window_size,"query": {"range":{"bidirectional_first_seen_ms": {"gte": time}}},"sort":{"bidirectional_first_seen_ms":{"order":"asc"}}}

        _early=self.es.search(index=file,body=_find_early_flow_body)
        _later=self.es.search(index=file,body=_find_later_flow_body)

        # 测试（结构化json）
        # print(json.dumps(_early, sort_keys=True, indent=4, separators=(',', ':'),ensure_ascii=False))
        # print("-------------------------------------------------------------")
        # print(json.dumps(_later['hits']['hits'][0], sort_keys=True, indent=4, separators=(',', ':'),ensure_ascii=False))

        _neighbour_less = _early['hits']['hits'][1]['_source']
        _neighbour_more = _later['hits']['hits'][1]['_source']

        if time - int(_neighbour_less['bidirectional_first_seen_ms']) > \
                        int(_neighbour_more['bidirectional_first_seen_ms']) - time:
            neighbour=_neighbour_more
        else:
            neighbour=_neighbour_less
        count=0
        for _ in neighbour:

            if(neighbour[_]*0.2 < flow[_] or neighbour[_]*0.2 > flow[_]):
                count += 1
        if count > self.threshold:
            return True
        else:
            return False