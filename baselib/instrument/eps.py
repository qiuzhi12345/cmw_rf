#-------------------------------------------------------------------------------
# Name:        eps.py
# Purpose:     DC Power Supply (E3633A)
# Created:     12/06/2018
# Author:      JTZ
# Copyright:   (c) Test 2017
#-------------------------------------------------------------------------------
import time
from baselib.loglib.log_lib import *
import platform

class eps(object):
    op_statlst=['OPEN',    #just open, not initialize for test
		'CLOSE',   #shutdown,need reopen again
		'RUN',     #begin measure
		'RDY',     #stop running,data is ready
		'ERROR',   #instrument is in error state, need reset
		'LOSE'];   #can't contact with it
    op_stat='LOSE';

    def __init__(self, device_name="E3633A", num_of_machine=0):
        if platform.platform().find("Linux") != -1:
            from GPIBImpl import GPIBLinux
            self.device = GPIBLinux.GPIBDevice(device_name,num_of_machine)
        else:
            from GPIBImpl import GPIBWindows
            self.device = GPIBWindows.GPIBDevice(device_name,num_of_machine)
        pass

    def isbusy(self,timeout=100):
    	for i in range(0,timeout):
    	    if self.device.ask('*OPC?').find("1") != -1:
    	        return False;
        	time.sleep(1);
    	return True;

    def wait(self):
        self.device.write('*WAI');
        while self.isbusy()==True:
            logdebug('EPS is still busy...');
        return True;

    def clean(self,timeout=10):
    	self.device.write('*CLS');
    	if False== self.isbusy(timeout):
    	    self.op_stat='OPEN';
    	    logdebug('EPS status clean ok!')
    	    return True;
        else:
            logdebug('EPS clean timeout %4.9f sec!'%timeout)
    	    self.op_stat='ERROR';
    	    return False;

    def reset(self,timeout=10):
    	self.device.write('*RST');
    	if False== self.isbusy(timeout):
    	    self.op_stat='OPEN';
    	    logdebug('EPS reset ok!');
    	    return True;
        else:
            logdebug('EPS reset timeout %4.9f sec!'%timeout)
    	    self.op_stat='ERROR';
    	    return False;

    def range(self, val=0, timeout=10):
        if val==0:
            self.device.write('VOLT:RANG P8V');
            if False== self.isbusy(timeout):
                logdebug('configured range: %s'%(self.device.ask('VOLT:RANG?')));
            else:
                logwarn('something wrong with the device')
        elif val==1:
            self.device.write('VOLT:RANG P20V');
            if False== self.isbusy(timeout):
                logdebug('configured range: %s'%(self.device.ask('VOLT:RANG?')));
            else:
                logwarn('something wrong with the device')
        else:            
            logwarn('input range parameter error, current range is: %s'%(self.device.ask('VOLT:RANG?')));

    def pwr(self, vol, cur): # directly generate the configured voltage with limited current
        '''
        parameter 'vol' and 'cur' should be float, int or string in the para_list
        '''
        para_list=['DEF','MIN','MAX']
        if (vol in para_list or type(vol)==float or type(vol)==int) and (cur in para_list or type(cur)==float or type(cur)==int):
            self.device.write('APPL %s, %s'%(vol, cur));
            while self.isbusy()==True:
                logdebug('EPS is still busy...');
            self.out_ena(1)
            logdebug('actual output voltage is %s(V), and limitted current is %s(A)'%(float(self.device.ask('MEAS:VOLT?')), cur))
        else:
            logwarn('Input Parameter Error!');

    def out_ena(self, en):
        if en:
            self.device.write('Output On');
            logdebug('EPS output enable!');
        else:
            self.device.write('Output Off');
            logdebug('EPS output disabled!');

    def meas(self, item):    # measure the actual output voltage or current
        if item == 'VOLT':
            logdebug('output voltage: %4.8fV'%(float(self.device.ask('MEAS:%s?'%item))));
            return float(self.device.ask('MEAS:%s?'%item))
        elif item == 'CURR':
            logdebug('total current: %4.8fA'%(float(self.device.ask('MEAS:%s?'%item))));
            return float(self.device.ask('MEAS:%s?'%item));
        else:
            logwarn('Command Error!');
            return False

    def ovcp(self, item='VOLT', val=5, en=1, timeout=10):
        '''
        item_list=['VOLT','CURR']
        '''
        if val=='MIN' or val=='MAX':
            self.device.write("%s:PROT %s"%(item, val));
            logdebug('%s tripped level: %s'%(item,val));
        elif (type(val)==float or type(val)==int):
            self.device.write("%s:PROT %f"%(item, val));
            logdebug('%s tripped level: %f'%(item, val));
        else:
            logwarn('Input tripped level error!');

        if False== self.isbusy(timeout):
            if en:
                self.device.write("%s:PROT:STAT ON"%item);
                logdebug('%s protection open'%item);
            else:
                self.device.write("%s:PROT:STAT OFF"%item);
                logdebug('%s protection closed'%item);            
        else:
            logwarn('something wrong with the device')

        #self.device.write("%s:PROT:CLE"%item);#clear the tripped OVP/OCP circuit

#    def conf(self):
#        #enable Status Byte and Standard Event Registers for interrupt generation
#        self.device.write('*SRE 32');  #Summary Register Enable: Standard Event bit=1
#        self.device.write('*ESE 60');  #Enabled Standard Event:Query Error, Device Error, Execution Error, Command Error
