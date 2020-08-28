from lib.nfstream import NFStreamer,NFPlugin
import struct
import numpy as np
from configparser import ConfigParser
from redis import Redis

class Detector(NFPlugin):
    '''
    def on_init(self, pkt):
        if pkt.raw_size >=0:
            print("a packet arrive")
            return 1
        else:
            return 0

    def on_update(self, pkt, flow):  # flow update with each packet belonging to the flow
        print(str(flow.id)+"is updating....")
        
        pass
    '''
    def updateValue(self, flow):

        pass

    def on_expire(self, entry):
        print(entry)



class DWS():
    def __init__(self,pool,attrlist):
        self.attrlist=attrlist
        self.conf=ConfigParser()
        self.conf.read("./config/config.ini")
        try:
            self.interface=self.conf['default']['interface']
        except:
            raise Exception("except a network interface number")
        self.r = Redis(connection_pool=pool)

    def matrix2Redis(self,r, vector, app):
        """Store given Numpy array 'vector' in Redis under list e.g tiktok-matrix"""

        h, w = vector.shape
        shape = struct.pack('>II', h, w)
        encoded = shape + vector.tobytes()
        # Store encoded data in Redis
        r.lpush(str(app)+"-matrix", encoded)
        return


    def json2redis(self,app,nfentry):
        item=[]
        for i in range(len(self.attrlist)):
            item.append(getattr(nfentry, self.attrlist[i]))
        res = np.asarray(item, dtype=np.float32)
        self.r.lpush(str(app),str(nfentry.to_json()))
        res = res.reshape(1,len(self.attrlist))
        # self.matrix2Redis(self.r,res,app)
        return res

    def getStream(self):
        pass

    def run(self,_buffer_slide,_buffer_od):
        my_capture_streamer = NFStreamer(source=self.interface,  # or live interface
                                         snaplen=65535,
                                         idle_timeout=30,
                                         active_timeout=300,
                                         plugins=(),
                                         dissect=True,
                                         max_tcp_dissections=10,
                                         max_udp_dissections=16,
                                         statistics=True,
                                         enable_guess=True,
                                         decode_tunnels=True,
                                         bpf_filter=None,
                                         promisc=True)

        for stream in my_capture_streamer:
            if stream.application_name == "HTTP.TikTok":
                res=self.json2redis(stream.application_name,stream)
                _buffer_od.put_nowait(res)
                _buffer_slide.put_nowait(stream.to_json())
            """
            add new app here
            """





