#-------------------------------------------------------------------------------
# Name:        mdo.py
# Purpose:     Mixed Domain Osilloscope (1GHz, 5GS/s)
# Created:     08/02/2017
# Copyright:   (c) Test 2017
#-------------------------------------------------------------------------------
import time
import re
import platform
from baselib.loglib.log_lib import *

class mdo(object):
    prim_addr = -1;
    op_statlst=['OPEN',    #just open, not initialize for test
		'CLOSE',   #shutdown,need reopen again
		'RUN',     #begin measure
		'RDY',     #stop running,data is ready
		'ERROR',   #instrument is in error state, need reset
		'LOSE'];   #can't contact with it
    op_stat='LOSE';


    def __init__(self, device_name="MDO3104"):
        from baselib.instrument.GPIBImpl import USBTMC
        self.device = USBTMC.TMCDevice(device_name)

    def isbusy(self,timeout=100):
	for i in range(0,timeout):
	    if self.device.ask('*OPC?').find("1") != -1:
	        return False;
    	    time.sleep(1);
	return True;

    def wait(self):
        self.device.write('*WAI');
        while self.isbusy()==True:
            loginfo('MDO3104 is still busy...')
	return True;

    def clean(self,timeout=10):
        self.device.write('*CLS');
        if False== self.isbusy(timeout):
            self.op_stat='OPEN';
            loginfo('MDO3104 status clean ok!')
            return True;
        else:
            loginfo('MDO3104 clean timeout %4.9f sec!'%timeout)
	    self.op_stat='ERROR';
	    return False;

    def reset(self,timeout=10):
    	self.device.write('*RST');
    	if False== self.isbusy(timeout):
    	    self.op_stat='OPEN';
    	    loginfo('MDO3104 reset ok!') 
    	    return True;
        else:
            loginfo('MDO3104 reset timeout %4.9f sec!'%timeout)
            self.op_stat='ERROR';
	    return False;

    def meas(self, mod, _type, _chn='CH1', _wei=1000,timeout=2):
        '''
        :param:
            - mod: 
                - 'IMMED': immediate read
                - 'MEASU': triggers automatic measurement 
            - _type: 'FREQ'
            - _chn: channel to be used
            - _wei: # of samples to be used for statistical measure, max value is 1000 
        '''
        type_res=''
        val_res=''
        self.device.write('MEASU:MEAS:SOU %s'%_chn);
        if mod== 'IMMED':
            self.device.write('MEASU:IMM:TYP %s'%_type);
            self.wait;
            type_res =self.device.ask('MEASU:IMM:TYP?');
            val_res  =self.device.ask('MEASU:IMM:VAL?');
            loginfo('TYPE: %s'%type_res)
            loginfo('VAL:  %s'%val_res)
            return type_res,val_res
        elif mod== 'MEASU':
            self.device.write('MEASU:MEAS:TYP %s'%_type);
            self.device.write('MEASU:STATI RESET');
            self.device.write('MEASU:STATI:WEI %d'%_wei);
            self.wait;
            time.sleep(timeout)
            type_res =self.device.ask('MEASU:MEAS:TYP?');
            unit_res =self.device.ask('MEASU:MEAS:UNI?');
            val_res  =self.device.ask('MEASU:MEAS:VAL?');
            mean_res =self.device.ask('MEASU:MEAS:MEAN?');
            min_res  =self.device.ask('MEASU:MEAS:MINI?');
            max_res  =self.device.ask('MEASU:MEAS:MAX?');
            std_res  =self.device.ask('MEASU:MEAS:STD?');
            loginfo('TYPE: %s'%type_res)       
            loginfo('VAL:  %s %s'%(val_res, unit_res.split('"')[1]))       
            loginfo('MEAN: %s %s'%(mean_res,unit_res.split('"')[1]))       
            loginfo('MIN:  %s %s'%(min_res, unit_res.split('"')[1]))       
            loginfo('MAX:  %s %s'%(max_res, unit_res.split('"')[1]))       
            loginfo('STD:  %s %s'%(std_res, unit_res.split('"')[1]))       
            return type_res,val_res,mean_res,min_res,max_res,std_res
        else:
            loginfo('MDO3104 command error!')

    def chn_sel(self, chn_en):
        #0x1-->ch1; 0x2-->ch2; 0x4-->ch3; 0x8-->ch4
        self.device.write('SELECT:CH1 %d;CH2 %d;CH3 %d;CH4 %d'%(chn_en&0x1, (chn_en>>1)&0x1, (chn_en>>2)&0x1, (chn_en>>3)&0x1));
        self.wait;

    def set_hscale(self, x_scale):
        self.device.write('HORizontal:MAIN:SCALE %dE-9'%x_scale);
        self.wait;

    def set_vscale(self, chn, y_scale, y_unit):
        #chn: 1,2,3,4
        #y_unit: V or A
        self.device.write('CH%d:SCAL %f; YUN %s'%(chn, y_scale, y_unit));
        self.wait;

    def set_prob_atten(self, atten):
        self.device.write('TRIG:EXT:PRO %s'%atten);
        self.wait;    

    def autoset(self):
        self.device.write(':AUTOSet EXECute')
        self.wait