from baselib.loglib.log_lib import *
import os, sys
import socket
import pandas as pd
from math import *
class MEM_TS(object):
    """docstring for common"""
    def __init__(self, channel):
        self.channel = channel

    def rd(self, reg_addr):
        for i in range(5):
            result = self.channel.req_com("cli_rl 0x%x"%(reg_addr), wr_end='\r\n')
            # result = self.channel.req_com("rl 0x%x"%(reg_addr), wr_end='\r\n')
            if result.find('value:') != -1:
            #logdebug("res:" + result)
                result = result.split('value:')[1]
                break
            elif i == 4:
                logwarn('rd fail,result:{} ,try agian {}'.format(result,i))
        try:
            result_int = int(result, 16)
            return result_int
        except:
            return result

    def wr(self, reg_addr, value):
        for i in range(5):
            result = self.channel.req_com("cli_wl 0x%x 0x%x"%(reg_addr, value), wr_end='\r\n')
            # result = self.channel.req_com("wl 0x%x 0x%x"%(reg_addr, value), wr_end='\r\n')
            if result.find('value:') != -1:
            # logdebug("res:" + result)
                result = result.split('value:')[1]
                break
            elif result.find('val:') != -1:
                result = result.split('val:')[1]
                break
            elif i == 4:
                logwarn('wr fail,result:{} ,try agian {}'.format(result,i))
        try:
            result_int = int(result, 16)
            return result_int
        except:
            return result

    def rdm(self, reg_addr, msb, lsb):
        result = self.rd(reg_addr);
        mask = (1<<(msb+1)) - (1<<lsb);
        try:
            result = (result & mask) >> lsb;
            # logdebug("resm:" + "0x%x"%result)
        except:
            logerror("mem reads " + "%s"%result)
        return result

    def wrm(self, reg_addr,msb,lsb,value,lsb_dis=0):
        result = self.rd(reg_addr);
        mask = (1<<(msb+1)) - (1<<lsb);
        try:
            if lsb_dis ==1:
                result = (result & ~mask) | ((value << lsb) & mask) | (((1<<(msb+1-lsb))-1)<<(lsb+16))
            else:
                result = (result & ~mask) | ((value << lsb) & mask)
            logdebug('{}'.format(result))
            return self.wr(reg_addr,result);
        except:
            logerror("mem write fail, reads  %s"%result)
            return