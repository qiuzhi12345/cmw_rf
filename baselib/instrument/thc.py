import time
from baselib.loglib.log_lib import *
import numpy as np
from baselib.test_channel.com import COM as com
import binascii
import os, sys
import time

class THC_table(object):
    func_head={
        'coil_rd':  "01 01 ",
        'coil_wr':  "01 05 ",
        'reg_rd' :  "01 03 ",
        'reg_wr' :  "01 06 "
    }

    device_ID={
              'device_ID_addr'  : ["0B B8", "0B B9", "0B BA", "0B BB"],
              'device_ID_code'  : [" 54 48", " 31 38", " 30 30"]   #TH 18 00
    }

    display_reg_cmd_list={              ## readable only with two bytes data
              'rd_temper_pv'    : "02 18",
              'rd_humid_pv'     : "02 E0",
              'rd_temper_sv'    : "00 10",
              'rd_humid_sv'     : "00 2E",
              'rd_assist_pv_set': "02 7C",
              'rd_assist_sv_set': "00 86",
              'temper_strength' : "01 D2",
              'humid_strength'  : "01 DC",
              'comm_protocol'   : "00 E6",
              'comm_code'       : "00 E8",
              'timeout'         : "00 EC"
    }

    rw_reg_cmd_list={                   ## readable and writable with two bytes data
              'set_temper'      : "07 4E",
              'set_humid'       : "07 4F",
              'temper_slope_set': "07 52",
              'humid_slope_set' : "07 53",
              'standby_time_h'  : "07 8C",
              'standby_time_m'  : "07 8D",
              'temper_range'    : "07 8E",
              'humid_range'     : "07 8F",
              'ordered_time_y'  : "1D B0",
              'ordered_time_M'  : "1D B1",
              'ordered_time_d'  : "1D B2",
              'ordered_time_h'  : "1D B3",
              'ordered_time_m'  : "1D B4"
    }

    rw_coil_cmd_list={
              'arrived_mode'   : "04 B3",  # 0: slope mode
              'stop_way'       : "04 B1",  # 0: hand operation
              'counting_mode'  : "04 B5",  # 0: immediately
              'working_mode'   : "03 E8",  # 0: by programme
              'control_mode'   : "04 B4",  # 0: temper and humid
              'poweroff_mode0' : "03 F3",
              'poweroff_mode1' : "03 F4",
              'poweroff_mode2' : "03 F5",
              'standby_setting': "04 B2",

              'launch'         : "00 D4",
              'switch'         : "04 B0",

              'stop'           : "00 D5"
    }

class thc(object):
    def __init__(self, channel, device="TH1800", nolog = False):
        '''
        channel:
            TH1800 currently should be connected to PC via serial port
            TEMI880 failed to connect to PC
        device:
            TH1800 : programmable temperature/humidity case
            TEMI880: non-programmable temperature/humidity case, with control by hand
        '''
        self.device = device
        #self.channel = channel
        if self.device == "TH1800":
            self.crc=0
            self.channel = channel
            self.channel.Hexmd = True
            self.channel.ser.baudrate = 9600
            self.channel.nolog = nolog
            self.device_name, self.device_seq=self.__get_device_ID()

            if self.device_name==device:
                loginfo('Find temperature/humidity controlor %s No.%s'%(device, self.device_seq))
                loginfo('More initial configuration for the device is needed!')
                #self.wr_register_cmd('temper_slope_set', 0xff)
                self.launch()
            elif self.device_name=='':
                logwarn('!!identification code of the device need to be written!!')
            else:
                logerror('!!!communication error!!!')
        elif self.device == "TEMI880":
            self.channel = ''
            self.device_name = "TEMI880"
            loginfo("input temperature parameter from touch screen")
        else:
            logwarn("temperature/humidity case is unknown, pls retry if no error at input")
            return False

    def temper_set(self, temper_in, scan_times, timeout = 10800):
        '''
        configure the working condition of temperature case: working temperature & duration

            : stat: 1-->work
                        -ret: temperature value
                    0-->fail
                        -ret:
                            0--> no response
                            1--> exit
                            2--> timeout
        '''
        stat = 0
        ret = 0
        if self.device_name=="TH1800":
            self.wr_register_cmd('set_temper', temper_in*10)
            timer_cnt=0
            cfg_time=0
            init_time=time.time()
            while True:
                temper_rcd=[]
                for i in range(scan_times):
                    if temper_in<0:
                        temper_rcd.append(int(self.rd_register_cmd('rd_temper_pv')-65536)/10.0)
                    else:
                        temper_rcd.append(int(self.rd_register_cmd('rd_temper_pv'))/10.0)
                temper_d=np.array(temper_rcd)
                timer_cnt=timer_cnt+1
                cfg_time=time.time()-init_time
                if abs(temper_d.mean()-float(temper_in))<0.1 and temper_d.std()<0.1:
                    loginfo("!!Actual temperature has reached the setting value!!")
                    stat = 1
                    ret = int(temper_in)
                    break
                elif int(cfg_time)>timeout:
                    stat = 0
                    ret = 2
                    logerror("Temperature configuration has been out of time!")
                    break
        elif self.device_name=="TEMI880":
            while True:
                IN = raw_input('\033[1;32mpls at SCREEN touch in temper %d, WHEN it reaches and becomes stable, input BELOW the value to start or \"exit\" to end whole test:\n'%int(temper_in))
                time.sleep(2)
                if IN=="exit":
                    logwarn("!!Exit the whole test!!")
                    stat = 0
                    ret = 1
                    break
                try:
                    stat = 1
                    ret = int(IN)
                    if ret != int(temper_in):
                        logwarn("actual input temper_value isn't in conformity with the suggested one in list")
                    break
                except:
                    logwarn("input configured temperature value")
                    continue
        else:
            logerror("!!device name of the temperature/humidity case is wrong!!")
        return stat, ret

    def hexShow(self, argv):
        result = ''
        hLen = len(argv)
        for i in xrange(hLen):
            hvol=ord(argv[i])
            hhex='%02x'%hvol
            result=result+hhex+' '
        return result

    def rd_register_cmd(self, cmd='set_temper'):
        self.channel.byte_end_cnt=7
        if THC_table.display_reg_cmd_list.has_key(cmd):
            rd_cmd_data = THC_table.func_head['reg_rd']+THC_table.display_reg_cmd_list['%s'%cmd]+" 00 01"
        elif THC_table.rw_reg_cmd_list.has_key(cmd):
            rd_cmd_data = THC_table.func_head['reg_rd']+THC_table.rw_reg_cmd_list['%s'%cmd]+" 00 01"
        else:
            logerror('!!input command failed in current function!!')
            return False
        loginfo("raw_rd_cmd_data: %s"%rd_cmd_data)
        rd_cmd_hex=bytearray.fromhex(rd_cmd_data)
        crc_modbus=self.__crc16_modbus(np.array(rd_cmd_hex))
        rd_cmd_data_out=rd_cmd_data+" %.2x %.2x"%(crc_modbus&0xff, (crc_modbus>>8)&0xff)
        loginfo("rd_cmd_data_out: %s"%(rd_cmd_data_out))
        data_tmp=self.channel.req_com(bytearray.fromhex(rd_cmd_data_out))
        data_res=self.hexShow(data_tmp).split(' ')[:-1]
        loginfo('res-->0x%s %d'%(data_res[self.channel.byte_end_cnt-4]+data_res[self.channel.byte_end_cnt-3],\
                 int(data_res[self.channel.byte_end_cnt-4]+data_res[self.channel.byte_end_cnt-3], 16)))
        return int(data_res[self.channel.byte_end_cnt-4]+data_res[self.channel.byte_end_cnt-3], 16)

    def wr_register_cmd(self, cmd='set_temper', val=35):
        self.channel.byte_end_cnt=8
        if not THC_table.rw_reg_cmd_list.has_key(cmd):
            logerror('!!input command failed in current function!!')
            return False
        val_res=" %.2x %.2x"%((val>>8)&0xff, val&0xff)
        wr_cmd_data = THC_table.func_head['reg_wr']+THC_table.rw_reg_cmd_list['%s'%cmd]+val_res
        loginfo("val_res:%s\nraw_wr_cmd_data: %s"%(val_res, wr_cmd_data))
        wr_cmd_hex=bytearray.fromhex(wr_cmd_data)
        crc_modbus=self.__crc16_modbus(np.array(wr_cmd_hex))
        wr_cmd_data_out=wr_cmd_data+" %.2x %.2x"%(crc_modbus&0xff, (crc_modbus>>8)&0xff)
        loginfo("wr_cmd_data_out: %s"%(wr_cmd_data_out))
        data_res=self.channel.req_com(bytearray.fromhex(wr_cmd_data_out))
        loginfo(self.hexShow(data_res))

    def rd_coil_cmd(self, cmd='arrived_mode'):
        self.channel.byte_end_cnt=6
        if not THC_table.rw_coil_cmd_list.has_key(cmd):
            logerror('!!input command failed in current function!!')
            return False
        rd_cmd_data = THC_table.func_head['coil_rd']+THC_table.rw_coil_cmd_list['%s'%cmd]+" 00 01"
        loginfo("raw_rd_cmd_data: %s"%rd_cmd_data)
        rd_cmd_hex=bytearray.fromhex(rd_cmd_data)
        crc_modbus=self.__crc16_modbus(np.array(rd_cmd_hex))
        rd_cmd_data_out=rd_cmd_data+" %.2x %.2x"%(crc_modbus&0xff, (crc_modbus>>8)&0xff)
        loginfo("rd_cmd_data_out: %s"%(rd_cmd_data_out))
        data_tmp=self.channel.req_com(bytearray.fromhex(rd_cmd_data_out))
        data_res=self.hexShow(data_tmp).split(' ')[:-1]
        loginfo('res-->0x%s %d'%(data_res[self.channel.byte_end_cnt-4]+data_res[self.channel.byte_end_cnt-3], \
                int(data_res[self.channel.byte_end_cnt-4]+data_res[self.channel.byte_end_cnt-3], 16)))
        return int(data_res[self.channel.byte_end_cnt-4]+data_res[-3], 16)

    def wr_coil_cmd(self, cmd='arrived_mode', val=35):
        self.channel.byte_end_cnt=8
        if not THC_table.rw_coil_cmd_list.has_key(cmd):
            logerror('!!input command failed in current function!!')
            return False
        val_res=" %.2x %.2x"%((val>>8)&0xff, val&0xff)
        wr_cmd_data = THC_table.func_head['coil_wr']+THC_table.rw_coil_cmd_list['%s'%cmd]+val_res
        loginfo("val_res:%s\nraw_wr_cmd_data: %s"%(val_res, wr_cmd_data))
        wr_cmd_hex=bytearray.fromhex(wr_cmd_data)
        crc_modbus=self.__crc16_modbus(np.array(wr_cmd_hex))
        wr_cmd_data_out=wr_cmd_data+" %.2x %.2x"%(crc_modbus&0xff, (crc_modbus>>8)&0xff)
        loginfo("wr_cmd_data_out: %s"%(wr_cmd_data_out))
        data_res=self.channel.req_com(bytearray.fromhex(wr_cmd_data_out))
        loginfo(self.hexShow(data_res))

    def _device_ID_conf(self, num):
        '''
        the module is to write identification code into the interior register for temperature/humidity case
        without any identification
        '''
        self.channel.byte_end_cnt=8
        id_val=" %.2x %.2x"%((num>>8)&0xff, num&0xff)

        for i in range(4):
            if i==3:
                code_val=id_val
            else:
                code_val=THC_table.device_ID['device_ID_code'][i]
            wr_cmd_data = THC_table.func_head['reg_wr']+THC_table.device_ID['device_ID_addr'][i]+code_val
            loginfo("raw_wr_cmd_data: %s"%wr_cmd_data)
            wr_cmd_hex=bytearray.fromhex(wr_cmd_data)
            crc_modbus=self.__crc16_modbus(np.array(wr_cmd_hex))
            wr_cmd_data_out=wr_cmd_data+" %.2x %.2x"%(crc_modbus&0xff, (crc_modbus>>8)&0xff)
            loginfo("wr_cmd_data_out: %s"%(wr_cmd_data_out))
            data_res=self.channel.req_com(bytearray.fromhex(wr_cmd_data_out))
            loginfo('data_res-->%s'%self.hexShow(data_res))

    def __get_device_ID(self):
        device_id=[]
        device_name=''
        device_seq=''
        self.channel.byte_end_cnt=7
        for i in range(4):
            rd_cmd_data = THC_table.func_head['reg_rd']+THC_table.device_ID['device_ID_addr'][i]+' 00 01'
            #loginfo("raw_rd_cmd_data: %s"%rd_cmd_data)
            rd_cmd_hex=bytearray.fromhex(rd_cmd_data)
            crc_modbus=self.__crc16_modbus(np.array(rd_cmd_hex))
            rd_cmd_data_out=rd_cmd_data+" %.2x %.2x"%(crc_modbus&0xff, (crc_modbus>>8)&0xff)
            #loginfo("rd_cmd_data_out: %s"%(rd_cmd_data_out))
            data_res=self.channel.req_com(bytearray.fromhex(rd_cmd_data_out))
            id_res=self.hexShow(data_res)
            #loginfo('id_res-->%s'%id_res)
            id_tmp=id_res.split(' ')
            device_id.append(chr(int('%s'%id_tmp[3], 16))+chr(int('%s'%id_tmp[4], 16)))
        loginfo(device_id)
        device_name=device_id[0]+device_id[1]+device_id[2]
        device_seq=device_id[3]
        return device_name, device_seq

    # def __crc16_le_byte(self, data_buf=[]):
    #     crc = (~(self.crc))&0xffff;
    #     for i in range(len(data_buf)):
    #         crc = crc16_le_table[(crc^data_buf[i])&0xff]^(crc>>8);
    #     logdebug("crc-->0x%x, 0x%x"%(crc, (~crc)&0xffff))
    #     return (~crc)&0xffff;

    # def __crc16_be_byte(self, data_buf=[]):
    #     crc = (~(self.crc))&0xffff;
    #     for i in range(len(data_buf)):
    #         crc = crc16_be_table[(crc>>8)^data_buf[i]]^((crc<<8)&0xffff);
    #     logdebug("crc-->0x%x, 0x%x"%(crc, (~crc)&0xffff))
    #     return (~crc)&0xffff;

    def __crc16_modbus(self, data_buf=[]):
        crc = (~(self.crc))&0xffff;
        for i in range(len(data_buf)):
            crc=crc^(data_buf[i]&0xff)
            for j in range(8):
                if (crc&0xffff)&0x0001:
                    crc=((crc>>1)^0xA001)
                else:
                    crc=(crc>>1)
        logdebug("0x%x"%(crc&0xffff))
        return crc

    def launch(self):
        self.wr_coil_cmd('launch', 0xFF00)
        self.wr_coil_cmd('switch', 0xFF00)

    def halt(self):
        self.wr_coil_cmd('stop', 0xFF00)
        self.wr_coil_cmd('switch', 0x0000)

