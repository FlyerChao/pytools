
import os
import re
import time
import sys
from datetime import datetime
import matplotlib.pyplot as plt   # 导入模块 matplotlib.pyplot，并简写成 plt
import numpy as np                # 导入模块 numpy，并简写成 np
from collections import Counter


def get_time_str(log_buf):
    var,tx_time = log_buf.split('[',1)
    tx_time,var = tx_time.split(']',1)
# [2021_08_27_00:26:06.422]
    try:
        # tx_timeArray = datetime.strptime(tx_time, "%Y_%m_%d_%H:%M:%S.%f")
        tx_timeArray = datetime.strptime(tx_time, "%Y-%m-%d %H:%M:%S.%f")
    except Exception as e:
        return None
    return tx_timeArray


def get_time_str(log_buf):
    var,tx_time = log_buf.split('[',1)
    tx_time,var = tx_time.split(']',1)

    tx_timeArray = datetime.strptime(tx_time, "%Y-%m-%d %H:%M:%S.%f")
    return tx_timeArray

def diff_tx_rx_time(tx_buf, rx_buf):

    var,tx_time = tx_buf.split('[',1)
    tx_time,var = tx_time.split(']',1)
    # print("var:",var)
    # print("tx_time:", tx_time)

    var,rx_time = rx_buf.split('[',1)
    rx_time,var = rx_time.split(']',1)
    # print("var:",var)
    # print("rx_time:", rx_time)

    tx_timeArray = datetime.strptime(tx_time, "%Y-%m-%d %H:%M:%S.%f")
    rx_timeArray = datetime.strptime(rx_time, "%Y-%m-%d %H:%M:%S.%f")
    # print("tx_timeArray:",tx_timeArray)
    # print("rx_timeArray:",rx_timeArray)
    tx_timestamp = float(time.mktime(tx_timeArray.timetuple()) * 1000.0 + tx_timeArray.microsecond / 1000.0)
    rx_timestamp = float(time.mktime(rx_timeArray.timetuple()) * 1000.0 + rx_timeArray.microsecond / 1000.0)

    time_diff = rx_timestamp - tx_timestamp
    return time_diff
