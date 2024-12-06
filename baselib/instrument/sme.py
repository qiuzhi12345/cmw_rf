#from visa import *
import time
import re
import platform
import fpformat
class sme(object):
    prim_addr = -1;
    op_statlst=['OPEN',    #just open, not initialize for test
		'CLOSE',   #shutdown,need reopen again
		'RUN',     #begin measure
		'RDY',     #stop running,data is ready
		'ERROR',   #instrument is in error state, need reset
		'LOSE'];   #can't contact with it
    op_stat='LOSE';
    def __init__(self,name='',timeout = 10):
        if platform.platform().find("Linux") != -1:
            from GPIBImpl import GPIBLinux
            self.device = GPIBLinux.GPIBDevice("") # HP
        else:
            from GPIBImpl import GPIBWindows
            self.device = GPIBWindows.GPIBDevice(name)
        pass
        '''name: sme1 or sme2,please check tag on sme instruments
        '''
        try:
            self.prim_addr=28;
            #object.__init__(self,self.prim_addr);
            print 'Open SME Successfully!';
            self.op_stat = 'OPEN';
            self.timeout = timeout;
        except:
            print 'Fail to operate GPIB bus!'
            return;
        print 'Initialize SME OK!'

    def isbusy(self,timeout=10):
	for i in range(0,timeout):
	    if '1'==self.ask('*OPC?'):
	        return False;
    	    time.sleep(1);
	return True;

    def reset(self):
        self.device.write("*RST");
        self.device.write("*CLS");
	if False== self.isbusy():
	    print 'SME reset ok!'
	    return True;
        else:
            print 'SME reset timeout %d sec!'%timeout;
	    return False;
    def getcurve(self):
        self.device.write("*TRG");
        result=self.device.ask("FETC?");
	result_lst=result.split(',');
        curve=[float(data) for data in result_lst];
        return curve;

    def display(self,cmdstr="READY"):
        self.device.write("DISP ON");
        self.device.write("DISP:TEXT \"%s\""%cmdstr);

    def disp_clr(self):
        self.device.write("DISP:TEXT:CLE");
    def op(self):
        self.device.write(":OUTP:STAT ON");
	self.device.write(":OUTP ON");
    def setpow(self,POW=30):
	self.device.write("SOUR:POW %s"%POW);
    def setfreq(self,FREQ=100E6):
	#self.write("SOUR:FREQ:FIX");
	self.device.write("SOUR:FREQ %s"%FREQ);
    def testfreqstop(self,FREQ):
	self.device.write("SOUR:FREQ:STOP %s"%FREQ);

    def rfoff(self):
	self.device.write(":OUTP OFF")
    def rfon(self):
	self.device.write(":OUTP:STAT ON")
