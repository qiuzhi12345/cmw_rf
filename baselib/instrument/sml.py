#File for GPIB VISA control of CMW
from visa import *
import time
import fpformat
import re

class sml(GpibInstrument):
    prim_addr=9;
    maxpwr=3;
    minpwr=-60;

    def isbusy(self,timeout=10):
	for i in range(0,timeout):
	    if '1'==self.ask('*OPC?'):
	        return False;	    
    	    time.sleep(1);
	return True; 
    
    def wait(self):
        self.write('*WAI');
        while self.isbusy()==True:
	      print 'SML is still busy...';
	return True;

    def clean(self,timeout=10):
	self.write('*CLS');
	if False== self.isbusy(timeout):
	    print 'SML status clean ok!'	    
	    return True;	    
        else:
            print 'SML clean timeout %d sec!'%timeout;
	    return False; 

    def reset(self,timeout=10):
	self.write('*RST');
	if False== self.isbusy(timeout):
	    print 'SML reset ok!'	    
	    return True;	    
        else:
            print 'SML reset timeout %d sec!'%timeout;
	    return False;
    
    def __init__(self,rf_chan,pwr,timeout=10): #IO response time in 5 seconds
	try:
           #get instrument list on gpib bus
	   instr_lst0=get_instruments_list();
	   instr_lst=[];
	   for i in range(0,len(instr_lst0)):
	       if re.findall(r'^GPIB',instr_lst0[i],re.M)!=[]:
	 	   instr_lst.append(instr_lst0[i]);
           if len(instr_lst)==0:
              print 'Find no instrument on GPIB Bus!';
              return;
           #try to get SML
	   self.prim_addr='';
           for i in range(0,len(instr_lst)):
               instr=instrument(instr_lst[i]);
               answer=instr.ask('*IDN?');
	       if answer.find('ROHDE&SCHWARZ,SML02')!=-1:
	          self.prim_addr=instr_lst[i];
		  print 'Find SML, Address is %s'%instr_lst[i];
	          break;

	   #check search result
	   if self.prim_addr=='':
	       print 'Sorry, find no SML exist!';
	       return;

	   #get handler for SML    
	   GpibInstrument.__init__(self,self.prim_addr);  
	   print 'Open SML Successfully!';
	   self.op_stat='OPEN';
	   self.timeout=timeout;
           
	except:
	   print "Fail to operate GPIB bus!"	
	   return;

        #instrument initialize
        self.reset();
        self.wait();
        self.clean();
        self.wait();
        self.set_chan(rf_chan);
        self.set_pwr(pwr);	   
	print 'Initialize SML OK!'

    def set_chan(self,rf_chan):
	self.write('SOUR:FREQ %dMHZ'%rf_chan); 
	return True;
	    
    def set_pwr(self,pwr):	    
	self.write('SOUR:POW %f'%pwr);    
	return True;
    
    def output_on(self):
	self.write('OUTPUT1 ON');
	return True;
    
    def output_off(self):
	self.write('OUTPUT1 OFF');
	return True;
    
    def get_maxpwr(self):
	return self.maxpwr;

    def get_minpwr(self):
	return self.minpwr;
