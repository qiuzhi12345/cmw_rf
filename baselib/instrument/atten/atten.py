#Filename: usb.py
import os, sys, time
import re
import subprocess
#sys.path.append('../../lib/atten/atten_ctrl/release')
# import atten_ctrl
from baselib.loglib.log_lib import *
import serial
#--------------------------------------------
# In Shell, some commands already registered:
# atten_ctrl.open(0), return handler
# atten_ctrl.close(handler)
# atten_ctrl.req(cmdstr)
#---------------------------------------------
#--------------------------------------------
# Internal function, generate command to set gpio
# gpio total num is 4, P0,P1,P2,P3, each Port have 8 bits
# command format:
# CmdType Para0, Para1, Para2, ..
#---------------------------------------------
#  CmdNo          Operation
#  1              LED 8bits correspond to 8 leds, 0 light 1 off
#  2              Hex display, range 0-255
#  3              Beep, set 1 or 0 repeatedly for generating sound
#  4              write P0
#  5              write P1
#  6              write P2
#  7              write P3
#  8              Switch off Hex display
#  9              read P0
#  0xa            read P1
#  0xb            read P2
#  0xc            read P3
#---------------------------------------------
global usbhandler

def open_att():
    global usbhandler
    usbhandler = 0
    try:
       usbhandler = atten_ctrl.open(0)
       if usbhandler==0: logerror('ERROR: failed to open USB')
       else: loginfo('attenuator connected via USB')
    except:
       logerror('ERROR: failed to open USB')
    return usbhandler

def close():
    global usbhandler
    try:
        result = atten_ctrl.close(usbhandler)
        if result!='OK!':
            logerror(result)
            return False
    except:
        logerror('ERROR: failed to close USB')
        return False
    loginfo('attenuator disconnected')
    return True

def req(cmdtype,value,value_op=0):
    global usbhandler
    try:
        result=atten_ctrl.req(usbhandler,cmdtype,value,value_op)
        if result!='OK!':
            logerror(result)
            return False
    except:
        logerror('Write Usb Port Denied!')
        return False
    return True

#######################################################
# Hex Display function
# Cmd format:
# first byte:  Hex_Disp_CmdType
# second byte: {Hex_Device_Id,Hex_data}
#######################################################
def hexdisp(hexdata):
    return req(2,hexdata,10) #last para represent repeat frequency

#######################################################
# Hex Display function
# Cmd format:
# first byte:  Hex_Disp_CmdType
# second byte: {}
#######################################################
def dispoff():
    return req(8,10)

#######################################################
# GPIO write function
# Cmd format:
# first byte:  GPIO_Write_CmdType
# second byte: {Bit7~Bit0}
# gpio_no reange: 0-3
#######################################################
def gpioset(gpio_no,value):
    return req(gpio_no+4,value)

#######################################################
# LED Lightening function
# Cmd format:
# first byte:  LED_OnOff_CmdType
# second byte: {Bit7~Bit0} 0:On, 1:off to switch led0-7
#######################################################
def ledswitch(value):
    return req(1,value)

#######################################################
# Beep function
# Cmd format:
# first byte: time length
# second byte: {Bit7~Bit0} 0:On, 1:off to switch led0-7
#######################################################
def beep(counter):
    toggle=1;
    for i in range(2*counter,0,-1):
        toggle =~ toggle
        result = req(3,toggle)
        if result==False:
            return False
        time.sleep(0.002)
    return True

#  P0,P2 not used for value and latch, because P0 and P2 used as memory inf,
#  data varied, so Hex display latch change to P30 and P31
#  P10~P14 for attenuation value ctrl
#  P15 for atten_0 latch enable
#  P16 for atten_1 latch enable
#  P17 for atten_2 latch enable
#  P34 for atten_3 latch enable
#######################################################
# Attenuator Control function
# input para: chan_id atten_id, atten_value
# total 2 attenuator_board, each board have two units,
# each units attenuation range is 30dB, so total attenuation
# range is 4*30=120dB
# atten_id:0-3, atten_value:0-30
#######################################################
def attenunitset(attenid,attenvalue):
    delaytime=0.05;
    #select latch en signal
    if   attenid==0:    latchen=1<<6;
    elif attenid==1:    latchen=1<<7;
    elif attenid==2:    latchen=1<<4;
    else:               latchen=1<<5;

    #ctrldata:bit0  0.5dB
    #ctrldata:bit1  1dB
    #ctrldata:bit2  2dB
    #ctrldata:bit3  4dB
    #ctrldata:bit4  8dB
    #ctrldata:bit5  16dB
    #current stage not consider 0.5dB
    #invert the phase because Hex device,get low 6bits as data
    ctrldata = (~int(attenvalue*2))&0x3f

    #latch data in attenuator
    #first step:set latch to zero and ctrl_value add on
    #unit0 and unit1 used P1 port as data and latch control
    #unit2 and unit3 use P1 port as data and P3.4,P3.5 as latch

    if False==gpioset(1,ctrldata):
       logerror('ERROR: failed to write to attenuator P1')
       return False
    time.sleep(delaytime)

    if False==gpioset(3,0xcf):
       logerror('ERROR: failed to write to attenuator P3')
       return False
    time.sleep(delaytime)

    #second step: latch to high and ctrl_vlaue keep
    if attenid==0 or attenid==1:
        if False==gpioset(1,ctrldata+latchen):
            logerror('ERROR: failed to write to attenuator P1')
            return False
    else:
        if False==gpioset(3,latchen+0xcf):
            logerror('ERROR: failed to write to attenuator P3')
            return False
    time.sleep(delaytime)

    #third step: latch to zero and ctrl_value keep
    if False==gpioset(1,ctrldata):
       logerror('ERROR: failed to write to attenuator P1')
       return False
    time.sleep(delaytime)

    #deal with special latchen for unit2 unit3
    if False==gpioset(3,0xcf):
       logerror('ERROR: failed to write to attenuator P3')
       return False
    time.sleep(delaytime)
    return True

#######################################################
# Final configure attenuation function
# input para: atten_value
# total 2 attenuator_board, each board have two units,
# each units attenuation range is 30dB, so total attenuation
# range is 4*30=120dB
# atten_value:0-120
#######################################################
def cfg(attenvalue):
    loginfo("setting attenuator values to %d" % attenvalue);
    if  attenvalue > 120:
        logerror('ERROR: attenuator value out of range (>120)')
        return False

    for ptr in range(4):
        if attenvalue>31:
            if False==attenunitset(ptr, 31):
               loginfo("ERROR:attenuator unit%d set fail!"%ptr)
               return False
            attenvalue -= 31
        elif attenvalue>0:
            if False==attenunitset(ptr, attenvalue):
               loginfo("ERROR:attenuator unit%d set fail!"%ptr)
               return False
            attenvalue=0;
        elif False==attenunitset(ptr, 0):
            loginfo("ERROR:attenuator unit%d set fail!"%ptr)
            return False

    loginfo("attenuator values are set")
    return True

def autotest(i=1, time_step=10):
    while i<100000:
        cfg(0)
        time.sleep(time_step)
        cfg(30)
        i=i+1

def autorun(net,mask,test_time,att_set=range(2,34,4), time_step=10):
	for att in att_set:
	    cfg(att)
	    time.sleep(time_step)

def iperfautorun(test_time,net,mask,filename,atten_set=range(0,40,2)):
	cfg(0)
	time.sleep(5)
	for atten in atten_set:
		cfg(atten)
        	#os.system('adb shell /system/bin/eagle_test trc 0x100')
	        os.system('adb shell /system/bin/eagle_test trc 0x20')
	        os.system('adb shell /data/data/com.magicandroidapps.iperf/bin/iperf -c 192.168.%d.%d -i 1 -t %d >> %s.csv'%(net,mask,test_time,filename))



def autoiperf(net,mask,test_time,numbers=range(8,20,4),time_sleep=10, mode='bg', router='dlink', nch=6):
	if mode == 'bg':
		data_rates=[0xC,0x8,0xD,0x9,0xE,0xA,0xF,0xB,0x3,0x2,0x1,0x0, 0x20]
		rates = ['54m', '48m', '36m', '24m', '18m', '12m', '9m', '6m', '11m_l', '5m_L', '2m_L', '1m_L', 'normal']
	else:
		data_rates=[0x13,0x12,0x11,0x10, 0x1B, 0x1A, 0x19, 0x18]
		rates = ['MCS3_L', 'MCS2_L', 'MCS1_L', 'MCS0_L', 'MCS3_S', 'MCS2_S', 'MCS1_S', 'MCS0_S']
	for j in range(0,len(data_rates)):
                cfg(0)
		outpath = './log/tx_rate_control/%s_%s/ch%d'%(router, mode, nch)
		outfile = '%s/tx_rate_%s.csv'%(outpath, rates[j])
		if not os.path.exists(outpath):
			os.makedirs(outpath)
		if os.path.exists(outfile):
			os.remove(outfile)
		time.sleep(10)
		for number in numbers:
	                cfg(number)
			if data_rates == 0x20:
			    os.system('adb shell /system/bin/eagle_test trc 0x20')
		        else:
                            os.system('adb shell /system/bin/eagle_test trc 0x100')
	                    os.system('adb shell /system/bin/eagle_test trc 0x%x'%data_rates[j])
			#os.system('adb logcat | grep 'esp_wifi' >> tx_rates%s.csv'%rates[j])
			f=open(outfile,'a+')
			f.write('****************** atten = %d *******************\n'%number)
			f.close()
                        #os.system('adb shell ping -i 0.2 -c 10 192.168.%d.%d'%(net,mask))
	                #os.system('adb shell /data/data/com.magicandroidapps.iperf/bin/iperf -c 192.168.%d.%d -i 1 -t %d >> tx_rate_%s.csv'%(net,mask,test_time,rates[j]))
			#argv = 'adb shell /data/data/com.magicandroidapps.iperf/bin/iperf -c 192.168.%d.%d -i 1 -t %d >> tx_rate_%s.csv'%(net,mask,test_time,rates[j])
			argv = 'adb shell /data/data/com.magicandroidapps.iperf/bin/iperf -c 192.168.%d.%d -i 1 -t %d '%(net,mask,test_time)
			print argv
			arg = argv.split(' ')
			print arg
			tmpfile=open("tmpoutput.txt", 'w')
			tmperr=open("tmperror.txt", 'w')
			iperf_proc = subprocess.Popen(arg,stdout=tmpfile,stderr=tmperr)
			print "iperf_proc started"
			print "enter sleep"
			time.sleep(test_time+5)
			print "out sleep"
			if iperf_proc.poll() is None:
				try:
					print "terminate iperf_proc"
					iperf_proc.terminate()
				except WindowsError:
					pass
			tmpfile.flush()
			tmpfile.close()
			tmperr.close()
			tmpfile = open("tmpoutput.txt", 'r')
			tmperr= open("tmperror.txt", 'r')
			iperf_output = tmpfile.readlines()
			err_output = tmperr.readlines()
			tmpfile.close()
			tmperr.close()
			print "=====iperf output========"
			print iperf_output
			print err_output
			f=open(outfile,'a+')
			f.writelines(iperf_output)
			f.close()
			os.system('adb shell eagle_test rdper >> %s'%(outfile))

			f=open(outfile,'a+')
			f.write('------- RSSI(ACK, DATA) = ')
			f.close()
			os.system('adb shell eagle_test rdrssi >> %s'%(outfile))

def autoiperf_rx(n,m,testtime,attenset=range(8,20,4), outfile='./rx_thruput/dlink/rx_rate_iperf.csv'):
	cfg(0)
	time.sleep(10)
	for at in attenset:
		cfg(at)
		f = open(outfile,'a+')
		f.write('****************** atten = %d *******************\n'%at)
		f.close()
	        os.system('iperf -c 192.168.%d.%d -i 1 -t %d -w 32K>> %s '%(n,m,testtime, outfile))

		f=open(outfile,'a+')
		f.write('------- RSSI(ACK, DATA) = ')
		f.close()
		os.system('adb shell eagle_test rdrssi >> %s'%(outfile))


def set_att(att=10, port=5, atten_fix=False):
    if att > 63:
        print "att must be 0~63 !!"
        return False
    # fix atte
    if atten_fix == True:
        if att >= 33 and (att-30+1)%4 == 0:
            att_t = att - 1
        elif att >= 33 and (att-30)%4 == 0:
            att_t = att + 1
        else:
            att_t = att
    else:
        att_t = att
    att_ser = serial.Serial(port-1)
    if att_ser.isOpen() == True:
        print 'com %d open suc'%(port)
    else:
        print 'com %d open fail'%(port)
        return False

    if att_t < 0x10:
        cmd_t = '7e7e100%x%x'%(att_t,0x10+att_t)
        exp_res_t = '7e7e200%x00%x'%(att_t, 0x20+att_t)
    else:
        cmd_t = '7e7e10%x%x'%(att_t,0x10+att_t)
        exp_res_t = '7e7e20%x00%x'%(att_t, 0x20+att_t)

##    print cmd_t
    cmd = cmd_t.decode("hex")
    exp_res =exp_res_t.decode("hex")
##    print cmd
    att_ser.write(cmd)
    time.sleep(0.1)
    res_num = att_ser.inWaiting()
##    print "res_num: %d"%(res_num)
    res = att_ser.read(res_num)
    att_ser.close()
##    print "%s == %s"%(exp_res,res)
    if res == exp_res :
        print "atte set %d suc !!"%(att)
        return True
    else :
        print "atte set %d fail !!"%(att)
        return False


