from baselib.loglib.log_lib import *
import os, sys
import socket
import pandas as pd
from math import *
from hal.hwregister.hwreg.all import HWREG

class MEM_TS(object):
    """docstring for common"""
    def __init__(self, channel):
        self.channel = channel

    def rd(self, reg_addr):
        for i in range(10):
            result = self.channel.req_com("rl 0x%x"%(reg_addr), wr_end='\r\n')
            if result.find('value:') != -1:
            #logdebug("res:" + result)
                result = result.split('value:')[1]
                break
            elif i == 9:
                logwarn('rd fail,result:{} ,try agian {}'.format(result,i))
        try:
            result_int = int(result, 16)
            return result_int
        except:
            return result

    def wr(self, reg_addr, value):
        for i in range(10):
            result = self.channel.req_com("wl 0x%x 0x%x"%(reg_addr, value), wr_end='\r\n')
            if result.find('value:') != -1:
            # logdebug("res:" + result)
                result = result.split('value:')[1]
                break
            elif i == 9:
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

    def wrm(self, reg_addr,msb,lsb,value):
        result = self.rd(reg_addr);
        mask = (1<<(msb+1)) - (1<<lsb);
        try:
            result = (result & ~mask) | ((value << lsb) & mask);
            return self.wr(reg_addr,result);
        except:
            logerror("mem write fail, reads  %s"%result)
            return

    def rfrd(self, reg_addr):
        for i in range(10):
            result = self.channel.req_com("rfrl 0x%x"%(reg_addr), wr_end='\r\n')
            if result.find('value:') != -1:
            #logdebug("res:" + result)
                result = result.split('value:')[1]
                break
            elif i == 9:
                logwarn('rd fail,result:{} ,try agian {}'.format(result,i))
        time.sleep(0.5)
        try:
            result_int = int(result, 16)
            return result_int
        except:
            return result


    def rfwr(self, reg_addr, value):
        for i in range(10):
            result = self.channel.req_com("rfwl 0x%x 0x%x"%(reg_addr, value), wr_end='\r\n')
            if result.find('value:') != -1:
            # logdebug("res:" + result)
                result = result.split('value:')[1]
                break
            elif i == 9:
                logwarn('wr fail,result:{} ,try agian {}'.format(result,i))
        time.sleep(0.5)
        try:
            result_int = int(result, 16)
            return result_int
        except:
            return result


    def rfrdm(self, reg_addr, msb, lsb):
        result = self.rfrd(reg_addr);
        mask = (1<<(msb+1)) - (1<<lsb);
        try:
            result = (result & mask) >> lsb;
            # logdebug("resm:" + "0x%x"%result)
        except:
            logerror("mem reads " + "%s"%result)
        return result

    def rfwrm(self, reg_addr,msb,lsb,value):
        result = self.rfrd(reg_addr);
        mask = (1<<(msb+1)) - (1<<lsb);
        try:
            result = (result & ~mask) | ((value << lsb) & mask);
            return self.rfwr(reg_addr,result);
        except:
            logerror("mem write fail, reads  %s"%result)
            return
class MEM(object):
    """docstring for common"""
    def __init__(self, channel, chipv = "ESP32"):
        self.chipv = chipv
        self.channel = channel

    def rd(self, reg_addr):
        result = self.channel.req_com("rd 0x%x"%(reg_addr))
        #logdebug("res:" + result)
        try:
            result_int = int(result, 16)
            return result_int
        except:
            return result

    def wr(self, reg_addr, value):
        result = self.channel.req_com("wr 0x%x 0x%x"%(reg_addr, value))
        # logdebug("res:" + result)
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
        return result;

    def rdmem(self,mem_addr,data_len):
        rm_hdr_len=(mem_addr&0x3);
        mem_addr_align=mem_addr-rm_hdr_len;
        align_data_len=data_len+rm_hdr_len;
        data_len=4*int(ceil(align_data_len*1.0/4));
        burst_len=32;
        burst_startaddr = mem_addr_align;
        burst_len_lst=[];
        burst_startaddr_lst=[]
        times=int(ceil(data_len*1.0/burst_len));
        while times>1:
            burst_len_lst.append(burst_len);
            burst_startaddr_lst.append(burst_startaddr);
            burst_startaddr = burst_startaddr+burst_len
            times=times-1;
            data_len=data_len-burst_len;
        burst_len_lst.append(data_len);
        burst_startaddr_lst.append(burst_startaddr);
        result_str='';
        cnt=0
        for datalen in burst_len_lst:
            rpt=1;
            while rpt==1:
               result=self.channel.req_com("RdMem 0x%x %d"%(burst_startaddr_lst[cnt],datalen));
               rs_lst=result.split();
               try:
                 rs_data=[int(i,16) for i in rs_lst];
                 if len(rs_data)!=int(ceil(datalen*1.0/4)):
                    rpt=1;
                 else:
                    rpt=0;
               except:
                 rpt=1;

            result_str=result_str+' '+result;
            cnt=cnt+1
        res_word = [int(i,16) for i in result_str.split()];
        res = [];
##        return result_str
        return str.split(result_str)
##        for i in range(0,align_data_len):
##           res.append(((res_word[i/4])>>(i%4*8))&0xff);
##        return res[rm_hdr_len:];

    def wrm(self, reg_addr,msb,lsb,value):
        result = self.rd(reg_addr);
        mask = (1<<(msb+1)) - (1<<lsb);
        try:
            result = (result & ~mask) | ((value << lsb) & mask);
            return self.wr(reg_addr,result);
        except:
            logerror("mem write fail, reads  %s"%result)
            return

    def accumiq(self,mem_addr,burst_len):
        result=self.channel.req_com("accumiq 0x%x %d"%(mem_addr,burst_len));
        return result

    def setmask(self, reg_addr, mask):
        return self.wr(reg_addr, self.rd(reg_addr) | mask)

    def clrmask(self, reg_addr, mask):
        return self.wr(reg_addr, self.rd(reg_addr) & (~mask))


class I2C(object):
    """docstring for I2C"""
    def __init__(self, channel, chipv = "ESP32"):
        self.chipv = chipv
        self.channel = channel

    def i2c_rd(self, block, host_id, reg_addr):
        if self.chipv=="CHIP722":
            host_id = 1
        # Warring!!! Don't change this commond, or else phy test will fail
        result = self.channel.req_com("ri 0x%x 0x%x 0x%x"%(block, host_id, reg_addr))
        # logdebug("res:" + result)
        try:
            result_int = int(result, 16)
            return result_int
        except:
            return result

    def i2c_wr(self, block, host_id, reg_addr, value):
        if self.chipv=="CHIP722":
            host_id = 1
        # Warring!!! Don't change this commond, or else phy test will fail
        result = self.channel.req_com("wi 0x%x 0x%x 0x%x 0x%x"%(block, host_id, reg_addr, value))
        # logdebug("res:" + result)
        return self.i2c_rd(block, host_id, reg_addr)

    def i2c_rdm(self, block, host_id, reg_addr, msb, lsb):
        result = self.i2c_rd(block, host_id, reg_addr);
        mask = (1<<(msb+1)) - (1<<lsb);
        try:
            result = (result & mask) >> lsb;
            # logdebug("resm:" + "0x%x"%result)
            return result;
        except:
            logerror("i2c mem reads " + "%s"%result)
            return result;

    def i2c_wrm(self, block, host_id, reg_addr, msb, lsb, value):
        result = self.i2c_rd(block, host_id, reg_addr);
        mask = (1<<(msb+1)) - (1<<lsb);
        try:
            result = (result & ~mask) | ((value << lsb) & mask);
            return self.i2c_wr(block, host_id, reg_addr,result);
        except:
            logerror("i2c mem write fail, reads %s"%result)
            return

class PBUS(object):
    """docstring for PBUS"""
    def __init__(self, channel, chipv = "ESP8266"):
        self.chipv = chipv
        self.channel = channel
        if chipv=="ESP32" or chipv=="CHIP72"  or chipv=="CHIP722" or chipv=="CHIP723" or chipv=="CHIP724" :
            self.pbus_dict = {
            "rfrx1" 	  : 0,
            "bb" 	      : 1,
            "dcoi"        : 2,
            "dcoq"        : 3,
            "rftx1" 	  : 4,
            "rftx2"       : 5
            }
        elif chipv=="ESP8266":
            self.pbus_dict = {
            "txbb1" 	  : 0,
            "txbb2" 	  : 1,
            "rfrx1"       : 2,
            "bbrx1"       : 3,
            "dcoi" 	      : 4,
            "dcoq"        : 5,
            "rftx1" 	  : 6,
            "rftx2"       : 7
            }

        self.pbus_en_dict = {
            "en1" 	  : 1,
            "en2" 	  : 2,
            "en3" 	  : 4
            }


    def pbus_debugmode(self):
        result=self.channel.req_com('pbus_debugmode');
        logdebug("res:" + result);
        return result

    def pbus_workmode(self):
        result=self.channel.req_com('pbus_workmode');
        logdebug("res:" + result);
        return result

    def pbus_rd(self,pbus_sel,pbus_en_sel):
        if type(pbus_sel)==type(''):
            pbus_no = self.pbus_dict[pbus_sel];
        else:
            pbus_no = pbus_sel;

        if type(pbus_en_sel)==type(''):
            bus_en = self.pbus_en_dict[pbus_en_sel];
        else:
            bus_en = pbus_en_sel;
        result=self.channel.req_com("pbus_rd %d %d"%(pbus_no,bus_en));
        logdebug("res:" + result);
        return int(result,16)

    def pbus_wr(self,pbus_sel,pbus_en_sel,value):
        if type(pbus_sel)==type(''):
            pbus_no = self.pbus_dict[pbus_sel];
        else:
            pbus_no = pbus_sel;

        if type(pbus_en_sel)==type(''):
            bus_en = self.pbus_en_dict[pbus_en_sel];
        else:
            bus_en = pbus_en_sel;
        result=self.channel.req_com("pbus %d %d %d"%(pbus_no,bus_en,value));
        logdebug("res:" + result);
        return self.pbus_rd(pbus_no,bus_en)

    def pbus_rm(self,pbus_sel,pbus_en_sel,msb,lsb):
        pbus_value=self.pbus_rd(pbus_sel,pbus_en_sel);
        mask=(2**(msb+1)-2**lsb)>>lsb;
        result=(pbus_value>>lsb)&mask;
        logdebug("resm:" + "0x%x"%result)
        return result

    def pbus_wm(self,pbus_sel,pbus_en_sel,msb,lsb,value):
        pbus_value=self.pbus_rd(pbus_sel,pbus_en_sel);
        mask1=2**(msb+1)-2**lsb;
        mask2=mask1^0xffffffff;
        new_data=(pbus_value&mask2)+((value<<lsb)&mask1);
        result=self.pbus_wr(pbus_sel,pbus_en_sel,new_data);
        logdebug("resm:" + "0x%x"%result)
        return result;


class CHIP_INFO(object):
    """docstring for CHIP_INFO"""
    def __init__(self, channel, INchipv = "AUTO"):
        self.channel = channel
        self.INchipv = INchipv
        self.chipv_list = ["ESP8266", "ESP32", "CHIP72", "CHIP722"]
        self.chipv = ""

    def get_chipv(self):
        '''
        Use UART Date register to determine the chip version
        '''

        if self.INchipv == "AUTO":
            if self.channel.isopen:
                self.__MEM = MEM(self.channel)
                try:
                    Uart_date = self.__MEM.rd(0x60000078) # Uart date
                    chip_version = self.__MEM.channel.req_com("get_chip_version", 1)
                    if chip_version == "chip722":
                        self.chipv =  "CHIP722"
                    elif chip_version == "chip723":
                        self.chipv = "CHIP723"
                    elif Uart_date == 0x062000:
                        self.chipv =  "ESP8266"
                    elif Uart_date == 0x15122500:
                        SPI_date = self.__MEM.rd(0x600023fc)
                        if SPI_date == 0x1702100:
                            self.chipv =  "CHIP72"
                        else:
                            self.chipv =  "ESP32"
                    else:
                        I2s_date = self.__MEM.rd(0x6000f0fc)
                        if I2s_date == 0x18092900:
                            self.chipv =  "CHIP722"
                        elif I2s_date == 0x19052500:
                            self.chipv =  "CHIP723"
                        else:
                            logwarn("can not get chipv, use default ESP32")
                            self.chipv =  "ESP32"
                except ValueError,e:
                    logwarn(e)
                    logwarn("rd register error, use default ESP32")
                    self.chipv =  "ESP32"

            else:
                logwarn("can not get chipv, use default ESP32")
                self.chipv =  "ESP32"
        elif self.INchipv in self.chipv_list:
            self.chipv =  self.INchipv
        loginfo("Dectect chip: %s"%(self.chipv))
        return self.chipv


class CHIP_ID(object):
    """
    docstring for CHIP_ID

    """
    def __init__(self, channel, chipv = "AUTO"):
        self.channel = channel
        self.chipv = chipv
        self.__hwreg = HWREG(self.channel, self.chipv)
        self.__mem = MEM(self.channel, self.chipv)

    def chip_mac(self):
        try:
            mac_id = ""
            if self.chipv in ("FPGA722", "FPGA723", "FPGA11ac"):
                return "0x00ecececececec"
            elif self.chipv == "ESP8266":
                word3 = self.__mem.rd(0x3ff0005c)
                word2 = self.__mem.rd(0x3ff00058)
                word1 = self.__mem.rd(0x3ff00054)
                word0 = self.__mem.rd(0x3ff00050)
                chip_flag = (word2 >>15) &0x1
                mac_type = (word2 >>12) &0x1
                if mac_type == 0:
                    macaddr0 = 0x18
                    macaddr1 = 0xfe
                    macaddr2 = 0x34
                else:
                    macaddr0 = (word3 >> 16)    & 0xff
                    macaddr1 = (word3 >> 8 )    & 0xff
                    macaddr2 = (word3      )    & 0xff

                macaddr3 = (word1 >> 8 )     & 0xff
                macaddr4 = (word1      )     & 0xff
                macaddr5 = (word0 >> 24)     & 0xff

                if (word2 & (1<<15)) == 0:
                    macaddr0 = word1 >> 16  & 0xff
                    macaddr1 = word1 >> 8   & 0xff
                    macaddr2 = word1        & 0xff
                    macaddr3 = word3 >> 8   & 0xff
                    macaddr4 = word3        & 0xff
                    macaddr5 = word2 >> 24  & 0xff

                mac_id = "0x%02x%02x%02x%02x%02x%02x"%( macaddr5,
                                                        macaddr4,
                                                        macaddr3,
                                                        macaddr2,
                                                        macaddr1,
                                                        macaddr0)


            elif self.chipv in ["ESP32", "CHIP72"]:
                mac_l = self.__hwreg.EFUSE.EFUSE_BLK0_RDATA1.rd_wifi_mac_crc_low
                mac_h = self.__hwreg.EFUSE.EFUSE_BLK0_RDATA2.rd_wifi_mac_crc_high
                mac_id = '0x%04x%08x'%(mac_h,mac_l)
            elif self.chipv in ["CHIP722"]:
                mac_l_tp = self.__hwreg.EFUSE.RD_MAC_SPI_8M_0.efuse_mac_0
                mac_h_tp = self.__hwreg.EFUSE.RD_MAC_SPI_8M_1.efuse_mac_1
                mac_l = socket.ntohl(mac_l_tp)
                mac_h = socket.ntohs(mac_h_tp)
                mac_id = '0x%08x%04x'%(mac_l,mac_h)
            return mac_id
        except ValueError,e:
            logwarn(e)
            return -1




