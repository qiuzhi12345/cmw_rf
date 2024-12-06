# -- coding: utf-8 --

import serial
import re;
import sys;
from baselib.loglib.log_lib import *
import subprocess
import platform
import threading
import time

class COM(object):
    '''

    :ComPort:
        串口号， 比如
            - 3 (Win)
            - /dev/ttyUSB0 (Linux/MACos)

    :ComPort:
        当前 ComPort

    :Hexmd:
        - True ：16进制模式
        - False ：aisc 码模式

    :endstr:
        在 交互模式下，接收命令结束符

        .. note::
            仅在 aisc 码模式 下有效。
            仅在 *line_end_cnt* = 0 下有效

    :line_end_cnt:
        在 交互模式下，接收行数。
        当 line_end_cnt = 0 的时候，为结束符模式

    :byte_end_cnt:
        接收数据的byte数。

        .. note::
            仅在 16进制模式 有效
    :initopen:
        auto open COM when class init

    '''
    def __init__(self, ComPort = '',
                        Hexmd = False,
                        endstr = '\n',
                        line_end_cnt = 0,
                        byte_end_cnt = 0,
                        nolog = False,
                        initopen = True,
                        bdw = 115200):
        '''
        '''
        self.ComPort = ''
        self.isopen = False
        self.Hexmd = Hexmd
        self.endstr = endstr
        self.line_end_cnt = line_end_cnt
        self.byte_end_cnt = byte_end_cnt
        self.nolog = nolog
        self.bdw = bdw
        #below param stops self.ser.timeout to be overwritten by req_com command if True
        self.req_com_timeout_block = False
        self.__conv_port(ComPort)
        if initopen:
           self.res_open = self.open(ComPort)

    def __conv_port(self, ComPort):
        if type(ComPort) == int:
            if platform.platform().find("Linux") != -1: # linux
              self.ComPort="/dev/ttyUSB%d"%ComPort
            elif platform.platform().find("Darwin") != -1: # mac os
              self.ComPort="/dev/%s"%ComPort
            else:
              self.ComPort="com%d"%ComPort # win
        elif type(ComPort) == str:
            self.ComPort = ComPort

    def open(self, ComPort = None):
        '''
        打开串口
        '''
        if ComPort != None:
            self.__conv_port(ComPort)
        # if serial.Serial(self.ComPort).isOpen() == True:
        #     self.isopen = True
        #     logdebug ('%r is open'%self.ComPort);
        # else:

        try:
            self.ser=serial.Serial(self.ComPort);
            # logdebug(self.ser.isOpen())
            # if self.ser.isOpen() == True:
            #     self.isopen = True
            #     logdebug('%r is open' % self.ComPort);
            #     return True

        except:
            logwarn ('Access %r is denied'%self.ComPort);
            return False
        self.ser.baudrate=self.bdw;
        self.ser.bytesize=serial.EIGHTBITS;
        self.ser.parity=serial.PARITY_NONE;
        self.ser.stopbits=serial.STOPBITS_ONE;
        self.ser.timeout=None;   #None:wait forever,0:non-block mode, x: timeout x seconds
        self.ser.xonxoff=0;
        self.ser.rtscts=0;
        self.ser.interCharTimeout=None;

        if self.ser.isOpen()==True:
            self.isopen = True
            logdebug ('%r is open'%self.ComPort);
        else:
            logwarn ('Can not open %r'%self.ComPort);

    def close(self):
        '''
        关闭串口
        '''
        try:
            self.ser.close();
            self.isopen = False
            logdebug('%r is closed'%self.ComPort);
        except:
            logwarn('The Port is not open ser');
            return False;


    def __req_com_imd(self, cmdstr='', timeout=10, endstr='\n', wr_end='\r', timeout_wait=10):
        '''
        :param:
            - timeout_wait: 
                - unit: seconds
                - newly added to prevent infinite loop if endstr is not '\n', default timeout is 10s 
        '''
        line = 0
        #set req_com_timeout_block to be True, so that timeout value can be set directly via self.ser.timeout
        if self.req_com_timeout_block == False:
            self.ser.timeout=timeout;
        self.ser.flushInput();
        self.ser.flushOutput();
        if self.Hexmd:
            cmd_send = cmdstr
        else:
            cmd_send = cmdstr+wr_end
        if self.nolog == False:
            logdebug(self.ComPort, "CMD->", cmd_send)
        self.ser.write(cmd_send.encode());

        if self.line_end_cnt != 0:
            respln = ''
            while True:
                line = line + 1
                resp=self.ser.readline();
                respln = respln + resp
                if line == self.line_end_cnt:
                    break
            return respln.strip("\n\r ")
        if self.byte_end_cnt != 0:
            respln=self.ser.read(self.byte_end_cnt)
            return respln

        if endstr == 'TS':
            self.ser.timeout = timeout
            respln = self.ser.readlines()
            return respln
        else:
            if endstr == "\n":
                respln=self.ser.readline();

            else:
                respln = ''
                t_bgn = time.time()  # record loop begin timing
                t_use = 0
                while t_use < timeout_wait:
                    resp=self.ser.readline()
                    respln = respln + resp
                    t_now = time.time() #record current time
                    t_use = t_now - t_bgn #calculate how long time loop has spent
                    if resp.find(endstr) != -1:
                        break
            if self.nolog == False:
                logdebug("REP<- %s"%(respln.strip("\n\r ")))
            return respln.strip("\n\r ")

    def req_com(self, cmdstr='',timeout=10, endstr='\n', wr_end='\r'):
        '''
        串口发送命令
        '''
        if self.ser.isOpen()==False:
            logerror('Com is not open!');
            return '';
        try:
            while True:
                result = self.__req_com_imd(cmdstr,timeout,endstr,wr_end)
                if result != "cmd not exist!":
                    break
                elif result != 'cmd   head error! Send Again!   \n':
                    break
                else:
                    #logwarn("%s cmd not exist!"%cmdstr)
                    logwarn(result)
            if result[0:15] == 'Plz run CmdStop':
                self.__req_com_imd('CmdStop',timeout,endstr,wr_end)
                result = self.__req_com_imd(cmdstr,timeout,endstr,wr_end)
            return result
        except:
            #logerror ("Unexpected error:" + str(sys.exc_info()))
            logerror ('fail to send command to com')
            self.ser.timeout=None;
            return ''

    def __serial_out_monitor(self):
        timeout_bk = self.ser.timeout
        self.ser.timeout = 0.8
        while True:
            if self.__q_flag == True:
                break
            try:
                resp=self.ser.readline()
                if resp != "":
                    if self.__mmd_log_flag == True:
                        self.__logfid.write(resp)
                    sys.stdout.write(resp)

            except:
                pass
        self.ser.timeout = timeout_bk

    def __serial_in_monitor(self):
        while True:
            if self.__q_flag == True:
                break
            self.__input = sys.stdin.readline()
            if self.__input.strip(" \n\r") == "Q":
                self.__q_flag = True
            else:
                if self.Hexmd:
                    cmd_send = self.__input
                else:
                    cmd_send = self.__input+'\r'
                self.ser.write(cmd_send.encode())
                if self.__mmd_log_flag == True:
                    self.__logfid.write(cmd_send)

    def start_mmd(self, logname = "", flush = True):
        '''
        monitor mode

        :logname:
            将log 保存至 文件，默认 “” 不保存。

        :flush:
            Flush serial before start
        '''
        if self.isopen == False:
            logerror("Com is not open!!")
            return
        logwarn("="*40)
        logwarn("COM monitor mode start!!")
        logwarn("\"Q\" to exit monitor mode!!")
        logwarn("="*40)
        if logname != "":
            self.__mmd_log_flag = True
            self.__logfid = open("./log/" + logname + "_serial.log", 'w')
        else:
            self.__mmd_log_flag = False
        self.__q_flag = False
        if flush == True:
            self.ser.flushInput();
            self.ser.flushOutput();
        td1 = threading.Thread(target=self.__serial_out_monitor)
        td0 = threading.Thread(target=self.__serial_in_monitor)
        td1.start()
        td0.start()
        while True:
            if td0.isAlive() == False and td1.isAlive() == False:
                break
            time.sleep(0.1)
        logwarn("COM monitor mode stop!!")
        if logname != "":
            self.__logfid.close()

    def deinit(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.deinit()
