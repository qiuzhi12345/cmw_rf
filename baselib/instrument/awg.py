#-------------------------------------------------------------------------------
# Name:        awg.py
# Purpose:     library of arbitrary waveform generator (33120A 15MHz)
# Created:     08/02/2017
# Author:      JTZ
# Copyright:   (c) Test 2017
#-------------------------------------------------------------------------------
import time
import re
import platform

class awg(object):
    op_statlst=['OPEN',    #just open, not initialize for test
		'CLOSE',   #shutdown,need reopen again
		'RUN',     #begin measure
		'RDY',     #stop running,data is ready
		'ERROR',   #instrument is in error state, need reset
		'LOSE'];   #can't contact with it
    op_stat='LOSE';


    def __init__(self, device_name="33120A", num_of_machine=0):
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
	      print 'AWG is still busy...';
	return True;

    def clean(self,timeout=10):
	self.device.write('*CLS');
	if False== self.isbusy(timeout):
	    self.op_stat='OPEN';
	    print 'AWG status clean ok!'
	    return True;
        else:
            print 'AWG clean timeout %4.9f sec!'%timeout;
	    self.op_stat='ERROR';
	    return False;

    def reset(self,timeout=10):
	self.device.write('*RST');
	if False== self.isbusy(timeout):
	    self.op_stat='OPEN';
	    print 'AWG reset ok!'
	    return True;
        else:
            print 'AWG reset timeout %4.9f sec!'%timeout;
	    self.op_stat='ERROR';
	    return False;

    def appl(self,name,freq,amp,offs):
        #uints of frequency, amplitude and offset are as follows:
        #               freq: KHZ
        #               amp:  VPP
        #               offs: V
        self.device.write('OUTP:LOAD INF');
        if name == 'SIN':
                self.device.write("FUNC:SHAP SIN");
                self.wait;
                self.device.write("FREQ %4.9f KHZ"%freq);
                self.wait;
                self.device.write("VOLT %4.9f VPP"%amp);
                self.wait;
                self.device.write("VOLT:OFFS %4.9f V"%offs);
                self.wait;
                print 'sine wave out!'
        elif name == 'SQU':
                self.device.write("FUNC:SHAP SQU");
                self.wait;
                self.device.write("FREQ %4.9f KHZ"%freq);
                self.wait;
                self.device.write("VOLT %4.9f VPP"%amp);
                self.wait;
                self.device.write("VOLT:OFFS %4.9f V"%offs);
                self.wait;
                print 'square wave out!'
        elif name == 'TRI':
                self.device.write("FUNC:SHAP TRI");
                self.wait;
                self.device.write("FREQ %4.9f KHZ"%freq);
                self.wait;
                self.device.write("VOLT %4.9f VPP"%amp);
                self.wait;
                self.device.write("VOLT:OFFS %4.9f V"%offs);
                self.wait;
                print 'tri-angle wave out!'
        elif name == 'RAMP':
                self.device.write("FUNC:SHAP RAMP");
                self.wait;
                self.device.write("FREQ %4.9f KHZ"%freq);
                self.wait;
                self.device.write("VOLT %4.9f VPP"%amp);
                self.wait;
                self.device.write("VOLT:OFFS %4.9f V"%offs);
                self.wait;
                print 'ramp wave out!'
        elif name == 'NOIS':
                self.device.write("FUNC:SHAP NOIS");
                self.wait;
                self.device.write("FREQ %4.9f KHZ"%freq);
                self.wait;
                self.device.write("VOLT %4.9f VPP"%amp);
                self.wait;
                self.device.write("VOLT:OFFS %4.9f V"%offs);
                self.wait;
                print 'random noise out!'
        elif name == 'DC':
                self.device.write("FUNC:SHAP DC");
                self.wait;
                #self.device.write("FREQ %d KHZ"%freq);
                #self.wait;
                #self.device.write("VOLT %d VPP"%amp);
                #self.wait;
                self.device.write("VOLT:OFFS %4.9f V"%offs);
                self.wait;
                print 'DC signal out!', offs
        else:
            print 'AWG command error!';
        #return float_res;

    def conf(self):
        #enable Status Byte and Standard Event Registers for interrupt generation
        self.device.write('*SRE 32');  #Summary Register Enable: Standard Event bit=1
        self.device.write('*ESE 60');  #Enabled Standard Event:Query Error, Device Error, Execution Error, Command Error

    #def __init__(self,ID_arr,timeout = 10):
