import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
def doSome(id,factor):
    VLAN = id
    FACTOR = factor
    attrVlan = {200: 632, 8: 628, 100: 2, 250: 6}
    vlanId = []
    times = []
    stedV = []
    RST = []
    PIAT_dev = []
    PIAT_mean = []
    Packets = []

    timesSum = 0
    packetSum = 0
    stedVSum = 0
    RSTSum = 0
    PIAT_devSum = 0
    PIAT_meanSum = 0

    yichang = 0

    df = pd.read_csv("amazon.csv")
    df.drop(columns=['id', 'app_protocol', 'master_protocol',
                     'src_ip_type', 'dst_ip_type'], inplace=True)

    for i in range(len(df)):
        vlanid = df.loc[i, 'vlan_id']

        if vlanid == VLAN:
            time = df.loc[i, 'bidirectional_duration_ms']

            stedv = df.loc[i, 'bidirectional_stdev_ip_ps']
            rst = df.loc[i, 'bidirectional_rst_packets']
            packets = df.loc[i, 'bidirectional_packets']

            piat = df.loc[i, 'bidirectional_stdev_piat_ms']
            piat_mean = df.loc[i, 'bidirectional_mean_piat_ms']
            if vlanid not in attrVlan.keys():
                attrVlan[vlanid] = 1
            else:
                attrVlan[vlanid] += 1

            packetSum += packets
            timesSum += time
            stedVSum += stedv
            RSTSum += rst
            PIAT_devSum += piat
            PIAT_meanSum += piat_mean

            # if vlanid not in attrVlan.keys():
            #     attrVlan[vlanid]=1
            # else:
            #     attrVlan[vlanid]+=1
            Packets.append(packets)
            times.append(time)
            vlanId.append(vlanid)
            stedV.append(stedv)
            RST.append(rst)
            PIAT_dev.append(piat)
            PIAT_mean.append(piat_mean)

            # print(len(times))

    timesSum /= attrVlan[VLAN]
    stedVSum /= attrVlan[VLAN]
    # RSTSum /= len(RST)
    PIAT_devSum /= attrVlan[VLAN]
    packetSum /= attrVlan[VLAN]
    PIAT_meanSum /= attrVlan[VLAN]

    print(attrVlan)
    print("平均时间：", timesSum)
    print("数据包数量：", packetSum)
    print("数据包平均到达时间:", PIAT_meanSum)
    print("数据包平均到达时间方差：", PIAT_devSum)
    print("rst数量:", RSTSum)

    for i in range(len(df)):
        flag = 0
        vlanid = df.loc[i, 'vlan_id']
        if vlanid == VLAN:
            rst = df.loc[i, 'bidirectional_rst_packets']
            if rst == 1:
                flag = 4
            else:
                time = df.loc[i, 'bidirectional_duration_ms']

                stedv = df.loc[i, 'bidirectional_stdev_ip_ps']

                packets = df.loc[i, 'bidirectional_packets']

                piat = df.loc[i, 'bidirectional_stdev_piat_ms']
                piat_mean = df.loc[i, 'bidirectional_mean_piat_ms']

                if ((packets / time) > (packetSum / timesSum) * FACTOR):
                    flag += 1
                if stedv > stedVSum * FACTOR:
                    flag += 1
                if piat_mean > PIAT_meanSum * FACTOR:
                    flag += 1
                if piat>PIAT_devSum*FACTOR:
                    flag+=1
            if flag >= 2:
                yichang += 1

    return yichang


