import time
from baselib.loglib.log_lib import *
import numpy as np
from baselib.test_channel.com import COM as com
import binascii
import os, sys
import time

speed_dir={
        2:  0xfa00,    #30DU/S
        1:  0xf230,    #12DU/S
        0:  0xc350    #3DU/S
    }

class smc(object):
    def __init__(self, channel,  nolog = False):
        '''
        channel:
            smc currently should be connected to PC via serial port

        '''
        self.channel = channel
        self.channel.Hexmd = True
        self.channel.ser.baudrate = 9600
        self.channel.ser.timeout = 10
        self.channel.nolog = nolog

        self.angle_current=0
        loginfo("current angle set as 0 angle")
        self.speed_ctrl = "speed_m"
        self.angle = 30
        #time.sleep(0.5)
        id=self.controller_id()
        if id=="":
            logerror("controller not connected")
        else:
            loginfo("controller_id = %s"%id)



    def run(self,angle=30,timeout=130):
        '''
        angle:  the angle which you want to run,if the angle >= 0,stepper motor direction is positive,
                else,stepper motor direction is negative
        speed_ctrl: stepper motor rev
                    0:  low speed
                    1:  middle speed
                    2:  high speed
        '''
        self.angle=abs(angle)
        if self.angle<=12:
            self.speed_ctrl=0
        elif self.angle>15 and self.angle<=30:
            self.speed_ctrl = 1
        else:
            self.speed_ctrl = 2
        self.bin8=0x31

        if angle>=0:
            self.bin7=0x1
            logdebug("stepper motor direction : positive ")
        else:
            self.bin7=0x2
            logdebug("stepper motor direction : negative ")

        while True:
            res=self.send_cmd()
            if res.split(" ")[0]=="b5":
                logerror("stepper motor does not turn,try again")
            elif res.split(" ")[0]=="b1":
                _timeout=time.time()+timeout
                while True:
                    res1=self.hexShow(self.channel.ser.read_all())
                    completer=res1.split(" ")[0]
                    if completer=="b0":
                        logdebug("stepper motor rotation completed")
                        break
                    if _timeout<time.time():
                        logerror("command reply %s abnormal,pls reboot"%completer)
                        break

                if angle>=0:
                    self.angle_current+=self.angle
                else:
                    self.angle_current-=self.angle

                logdebug("current angle : %d"%(self.angle_current))
                break
            else:
                logerror("controller abnormal,pls reboot")
                break
        time.sleep(1)

    def run_continue(self,speed_ctrl=2,direction=0):
        '''
        speed_ctrl: stepper motor rev
                    0:  low speed
                    1:  middle speed
                    2:  high speed
        direction:  0:run positive
                    1:run nagetive
        '''
        self.speed_ctrl=speed_ctrl
        self.bin8=0x30

        if direction==0:
            self.bin7=0x1
            logdebug("stepper motor direction : positive ")
        else:
            self.bin7=0x2
            logdebug("stepper motor direction : negative ")
        res=self.send_cmd()

    def stop(self):
        self.bin7=0x3
        self.send_cmd()

    def angle_origin_set(self):
        self.angle_current=0
        logdebug("current angle set as 0 angle")

    def return_origin_angle(self):
        logsetlevel('ERROR')
        cur_angle=self.angle_current
        if cur_angle>=0:
            self.run(angle=-cur_angle)
        else:
            self.run(angle=abs(cur_angle))
        logsetlevel('DEBUG')
        self.angle_current=0
        logdebug("current angle : %d"%(self.angle_current))

    def send_cmd(self):
        speed=speed_dir[self.speed_ctrl]
        pulse_sum=self.angle*400
        bin1=0xba                       #data header,BA is the real-time control command
        bin2=0x1                        #01:single step mode
        bin3=(speed>>8)&0xff
        bin4=speed&0xff
        bin5=0x0                        #controller adress
        bin6=0x1
        bin7=0x1                        #controller state,01:run positive,02:run nagetive,03:stop
        bin8=0x31
        bin9=(pulse_sum>>16)&0xff
        bin10=(pulse_sum>>8)&0xff
        bin11=pulse_sum&0xff
        bin12=0x0
        bin13=0xc8
        bin14=0x0
        bin15=0xc8
        bin16=bin1^bin2^bin3^bin4^bin5^bin6^self.bin7^self.bin8^bin9^bin10^bin11^bin12^bin13^bin14^bin15             #crc check
        bin17=0xfe                                                                                              #data ender
        str_bin="%.2x %.2x %.2x %.2x %.2x %.2x %.2x %.2x %.2x %.2x %.2x %.2x %.2x %.2x %.2x %.2x %.2x"%(bin1,
                bin2,bin3,bin4,bin5,bin6,self.bin7,self.bin8,bin9,bin10,bin11,bin12,bin13,bin14,bin15,bin16,bin17)
        logdebug("send command:%s"%str_bin)

        self.channel.ser.flushInput()
        self.channel.ser.flushOutput()

        cmd_out=bytearray.fromhex(str_bin)
        self.channel.ser.write(cmd_out)
        time.sleep(0.2)
        data_hex=self.channel.ser.read_all()
        data_res=self.hexShow(data_hex)

        if data_res=="":
            logerror("send command fail")
        else:
            logdebug("command return:%s"%data_res)

        return data_res

    def hexShow(self, argv):
        result = ''
        hLen = len(argv)
        for i in xrange(hLen):
            hvol=ord(argv[i])
            hhex='%02x'%hvol
            result=result+hhex+' '
        return result

    def controller_id(self):
        self.channel.ser.flushOutput()
        self.channel.ser.flushInput()
        self.channel.ser.write(bytearray.fromhex("B6 00 08 BE FE"))
        time.sleep(1)
        data_hex=self.channel.ser.read_all()
        data_res=self.hexShow(data_hex)
        return data_res
